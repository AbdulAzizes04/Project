"""
Optimizer Factory supporting AdamW, SGD, and Lion optimizers.
"""

import torch
import torch.optim as optim
from typing import Iterable
from earth_vision_x.app.config.constants import SupportedOptimizers

# Lion Optimizer implementation (EvoLved Sign Momentum)
class Lion(optim.Optimizer):
    def __init__(self, params: Iterable[torch.nn.Parameter], lr: float = 1e-4, betas=(0.9, 0.99), weight_decay: float = 0.0):
        defaults = dict(lr=lr, betas=betas, weight_decay=weight_decay)
        super().__init__(params, defaults)

    @torch.no_grad()
    def step(self, closure=None):
        loss = None
        if closure is not None:
            with torch.enable_grad():
                loss = closure()

        for group in self.param_groups:
            for p in group['params']:
                if p.grad is None:
                    continue
                grad = p.grad
                state = self.state[p]

                if len(state) == 0:
                    state['exp_avg'] = torch.zeros_like(p)

                exp_avg = state['exp_avg']
                beta1, beta2 = group['betas']

                # Weight decay
                if group['weight_decay'] > 0:
                    p.mul_(1 - group['lr'] * group['weight_decay'])

                # Update momentum and parameter
                update = exp_avg.mul(beta1).add(grad, alpha=1 - beta1)
                p.add_(torch.sign(update), alpha=-group['lr'])
                exp_avg.mul_(beta2).add_(grad, alpha=1 - beta2)

        return loss

class OptimizerFactory:
    @staticmethod
    def get_optimizer(model_params, opt_name: str | SupportedOptimizers = SupportedOptimizers.ADAMW, lr: float = 1e-4) -> torch.optim.Optimizer:
        if opt_name == SupportedOptimizers.SGD or "SGD" in str(opt_name):
            return optim.SGD(model_params, lr=lr, momentum=0.9, weight_decay=1e-4)
        elif opt_name == SupportedOptimizers.LION or "Lion" in str(opt_name):
            return Lion(model_params, lr=lr, weight_decay=1e-2)
        else:
            return optim.AdamW(model_params, lr=lr, weight_decay=1e-4)
