import torch
import numpy as np
import logging
import hydra
from hydra.utils import instantiate
import model.metric as module_metric
from trainer import Trainer


# fix random seeds for reproducibility
SEED = 123
torch.manual_seed(SEED)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
np.random.seed(SEED)

logger = logging.getLogger('train')

@hydra.main(config_path='conf/', config_name='config')
def main(config):
    # setup data_loader instances
    data_loader, valid_data_loader = instantiate(config.data_loader)

    # build model architecture, then print to console
    model = instantiate(config.arch)
    logger.info(model)

    # get function handles of loss and metrics
    criterion = instantiate(config.loss)
    metrics = [getattr(module_metric, met) for met in config['metrics']]

    # build optimizer, learning rate scheduler. delete every lines containing lr_scheduler for disabling scheduler
    trainable_params = filter(lambda p: p.requires_grad, model.parameters())
    optimizer = instantiate(config.optimizer, trainable_params)
    lr_scheduler = instantiate(config.lr_scheduler, optimizer)

    trainer = Trainer(model, criterion, metrics, optimizer,
                      config=config,
                      data_loader=data_loader,
                      valid_data_loader=valid_data_loader,
                      lr_scheduler=lr_scheduler)

    trainer.train()


if __name__ == '__main__':
    # pylint: disable=no-value-for-parameter
    main()
