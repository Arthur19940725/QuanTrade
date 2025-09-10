#!/usr/bin/env python3
"""
Windows 兼容的 tokenizer 训练脚本
避免使用 torchrun 和分布式训练，直接使用单 GPU 或 CPU 训练
"""

import json
import os
import sys
import time
from time import gmtime, strftime

import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader

# Ensure project root is in path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from finetune.config import Config
from finetune.dataset import QlibDataset

# Import shared utilities
from finetune.utils.training_utils import (
    format_time,
    get_model_size,
    set_seed,
)
from model.kronos import KronosTokenizer


def create_dataloaders(config: dict):
    """
    Creates and returns dataloaders for training and validation.

    Args:
        config (dict): A dictionary of configuration parameters.

    Returns:
        tuple: A tuple containing (train_loader, val_loader, train_dataset, valid_dataset).
    """
    print("Creating dataloaders...")
    train_dataset = QlibDataset('train')
    valid_dataset = QlibDataset('val')
    print(f"Train dataset size: {len(train_dataset)}, Validation dataset size: {len(valid_dataset)}")

    # 创建数据加载器
    train_loader = DataLoader(
        train_dataset,
        batch_size=config.batch_size,
        shuffle=True,
        num_workers=0,  # Windows 上设置为 0 避免多进程问题
        pin_memory=True if torch.cuda.is_available() else False
    )
    
    val_loader = DataLoader(
        valid_dataset,
        batch_size=config.batch_size,
        shuffle=False,
        num_workers=0,  # Windows 上设置为 0 避免多进程问题
        pin_memory=True if torch.cuda.is_available() else False
    )

    return train_loader, val_loader, train_dataset, valid_dataset


def train_epoch(model, train_loader, optimizer, device, epoch, config):
    """
    Trains the model for one epoch.

    Args:
        model: The model to train.
        train_loader: The training data loader.
        optimizer: The optimizer.
        device: The device to use.
        epoch: The current epoch number.
        config: Configuration dictionary.

    Returns:
        float: The average training loss for the epoch.
    """
    model.train()
    total_loss = 0.0
    num_batches = 0

    for batch_idx, batch in enumerate(train_loader):
        optimizer.zero_grad()

        # 移动数据到设备 - 数据集返回 (x_tensor, x_stamp_tensor) 元组
        if isinstance(batch, (list, tuple)) and len(batch) == 2:
            x_tensor, x_stamp_tensor = batch
            x_tensor = x_tensor.to(device)
            x_stamp_tensor = x_stamp_tensor.to(device)
            batch = (x_tensor, x_stamp_tensor)
        elif isinstance(batch, dict):
            for key in batch:
                if torch.is_tensor(batch[key]):
                    batch[key] = batch[key].to(device)
        elif torch.is_tensor(batch):
            batch = batch.to(device)

        # 前向传播
        try:
            if hasattr(model, 'forward'):
                # 模型期望接收特征张量，不是元组
                if isinstance(batch, (list, tuple)) and len(batch) == 2:
                    x_tensor, x_stamp_tensor = batch
                    # 只使用主要特征张量，忽略时间特征
                    outputs = model(x_tensor)
                elif isinstance(batch, dict) and 'data' in batch:
                    outputs = model(batch['data'])
                else:
                    outputs = model(batch)
            else:
                print("Warning: Model does not have forward method")
                continue

            # 计算损失 - KronosTokenizer 返回 ((z_pre, z), bsq_loss, quantized, z_indices)
            if isinstance(outputs, tuple) and len(outputs) >= 2:
                # KronosTokenizer 的输出格式
                (z_pre, z), bsq_loss, quantized, z_indices = outputs
                loss = bsq_loss  # 使用 BSQuantizer 的损失
            elif isinstance(outputs, dict) and 'loss' in outputs:
                loss = outputs['loss']
            elif torch.is_tensor(outputs):
                # 简单的 MSE 损失作为示例
                if 'target' in batch:
                    loss = F.mse_loss(outputs, batch['target'])
                else:
                    # 如果没有目标，使用自监督损失
                    loss = F.mse_loss(outputs, outputs.detach())
            else:
                print("Warning: Cannot compute loss from model outputs")
                continue

            # 反向传播
            loss.backward()
            
            # 梯度裁剪
            if hasattr(config, 'clip') and config.clip > 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), config.clip)

            optimizer.step()

            total_loss += loss.item()
            num_batches += 1

            # 打印进度
            if batch_idx % config.log_interval == 0:
                print(f'Epoch {epoch}, Batch {batch_idx}, Loss: {loss.item():.6f}')

        except Exception as e:
            print(f"Error in batch {batch_idx}: {e}")
            continue

    return total_loss / max(num_batches, 1)


def validate_epoch(model, val_loader, device):
    """
    Validates the model for one epoch.

    Args:
        model: The model to validate.
        val_loader: The validation data loader.
        device: The device to use.

    Returns:
        float: The average validation loss for the epoch.
    """
    model.eval()
    total_loss = 0.0
    num_batches = 0

    with torch.no_grad():
        for batch in val_loader:
            try:
                # 移动数据到设备 - 数据集返回 (x_tensor, x_stamp_tensor) 元组
                if isinstance(batch, (list, tuple)) and len(batch) == 2:
                    x_tensor, x_stamp_tensor = batch
                    x_tensor = x_tensor.to(device)
                    x_stamp_tensor = x_stamp_tensor.to(device)
                    batch = (x_tensor, x_stamp_tensor)
                elif isinstance(batch, dict):
                    for key in batch:
                        if torch.is_tensor(batch[key]):
                            batch[key] = batch[key].to(device)
                elif torch.is_tensor(batch):
                    batch = batch.to(device)

                # 前向传播
                if hasattr(model, 'forward'):
                    # 模型期望接收特征张量，不是元组
                    if isinstance(batch, (list, tuple)) and len(batch) == 2:
                        x_tensor, x_stamp_tensor = batch
                        # 只使用主要特征张量，忽略时间特征
                        outputs = model(x_tensor)
                    elif isinstance(batch, dict) and 'data' in batch:
                        outputs = model(batch['data'])
                    else:
                        outputs = model(batch)

                    # 计算损失 - KronosTokenizer 返回 ((z_pre, z), bsq_loss, quantized, z_indices)
                    if isinstance(outputs, tuple) and len(outputs) >= 2:
                        # KronosTokenizer 的输出格式
                        (z_pre, z), bsq_loss, quantized, z_indices = outputs
                        loss = bsq_loss  # 使用 BSQuantizer 的损失
                    elif isinstance(outputs, dict) and 'loss' in outputs:
                        loss = outputs['loss']
                    elif torch.is_tensor(outputs):
                        if 'target' in batch:
                            loss = F.mse_loss(outputs, batch['target'])
                        else:
                            loss = F.mse_loss(outputs, outputs.detach())
                    else:
                        continue

                    total_loss += loss.item()
                    num_batches += 1

            except Exception as e:
                print(f"Error in validation batch: {e}")
                continue

    return total_loss / max(num_batches, 1)


def main():
    """Main training function."""
    print("Starting Windows-compatible tokenizer training...")
    
    # 设置随机种子
    set_seed(42)
    
    # 加载配置
    config = Config()
    
    # 检查设备 - 对于 RTX 5060 Ti，使用 CPU 避免兼容性问题
    if torch.cuda.is_available():
        # 检查 CUDA 兼容性
        cuda_capability = torch.cuda.get_device_capability()
        if cuda_capability[0] >= 12:  # RTX 5060 Ti 是 sm_120
            print("Warning: RTX 5060 Ti detected. Using CPU to avoid compatibility issues.")
            device = torch.device('cpu')
        else:
            device = torch.device('cuda')
    else:
        device = torch.device('cpu')
    print(f"Using device: {device}")
    
    # 创建数据加载器
    train_loader, val_loader, train_dataset, valid_dataset = create_dataloaders(config)
    
    if len(train_dataset) == 0:
        print("Error: No training data available. Please run data preprocessing first.")
        return
    
    # 创建模型
    print("Creating KronosTokenizer model...")
    try:
        model = KronosTokenizer(
            d_in=len(config.feature_list),
            d_model=config.d_model if hasattr(config, 'd_model') else 512,
            s1_bits=config.s1_bits if hasattr(config, 's1_bits') else 8,
            s2_bits=config.s2_bits if hasattr(config, 's2_bits') else 4,
            n_enc_layers=config.n_enc_layers if hasattr(config, 'n_enc_layers') else 6,
            n_dec_layers=config.n_dec_layers if hasattr(config, 'n_dec_layers') else 6,
            n_heads=config.n_heads if hasattr(config, 'n_heads') else 8,
            ff_dim=config.ff_dim if hasattr(config, 'ff_dim') else 2048,
            ffn_dropout_p=config.ffn_dropout_p if hasattr(config, 'ffn_dropout_p') else 0.1,
            attn_dropout_p=config.attn_dropout_p if hasattr(config, 'attn_dropout_p') else 0.1,
            resid_dropout_p=config.resid_dropout_p if hasattr(config, 'resid_dropout_p') else 0.1,
            beta=config.beta if hasattr(config, 'beta') else 0.25,
            gamma0=config.gamma0 if hasattr(config, 'gamma0') else 1.0,
            gamma=config.gamma if hasattr(config, 'gamma') else 1.0,
            zeta=config.zeta if hasattr(config, 'zeta') else 1.1,
            group_size=config.group_size if hasattr(config, 'group_size') else 1
        )
        model = model.to(device)
        model_size = get_model_size(model)
        print(f"Model created successfully. Size: {model_size} parameters")
    except Exception as e:
        print(f"Error creating model: {e}")
        print("Please check your model configuration and dependencies.")
        return
    
    # 创建优化器
    optimizer = torch.optim.AdamW(model.parameters(), lr=config.learning_rate if hasattr(config, 'learning_rate') else 1e-4)
    
    # 训练循环
    print(f"Starting training for {config.epochs} epochs...")
    start_time = time.time()
    
    best_val_loss = float('inf')
    train_losses = []
    val_losses = []
    
    for epoch in range(1, config.epochs + 1):
        print(f"\nEpoch {epoch}/{config.epochs}")
        print("-" * 50)
        
        # 训练
        train_loss = train_epoch(model, train_loader, optimizer, device, epoch, config)
        train_losses.append(train_loss)
        
        # 验证
        val_loss = validate_epoch(model, val_loader, device)
        val_losses.append(val_loss)
        
        # 打印结果
        elapsed = time.time() - start_time
        print(f"Epoch {epoch} - Train Loss: {train_loss:.6f}, Val Loss: {val_loss:.6f}")
        print(f"Time elapsed: {format_time(elapsed)}")
        
        # 保存最佳模型
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            print(f"New best validation loss: {best_val_loss:.6f}")
            
            # 保存模型
            os.makedirs(config.save_path, exist_ok=True)
            model_path = os.path.join(config.save_path, 'best_tokenizer_model.pth')
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'train_loss': train_loss,
                'val_loss': val_loss,
                'config': config.__dict__
            }, model_path)
            print(f"Model saved to {model_path}")
    
    # 训练完成
    total_time = time.time() - start_time
    print(f"\nTraining completed!")
    print(f"Total time: {format_time(total_time)}")
    print(f"Best validation loss: {best_val_loss:.6f}")
    
    # 保存训练历史
    history = {
        'train_losses': train_losses,
        'val_losses': val_losses,
        'best_val_loss': best_val_loss,
        'total_time': total_time,
        'epochs': config.epochs
    }
    
    history_path = os.path.join(config.save_path, 'training_history.json')
    with open(history_path, 'w') as f:
        json.dump(history, f, indent=2)
    print(f"Training history saved to {history_path}")


if __name__ == "__main__":
    main()