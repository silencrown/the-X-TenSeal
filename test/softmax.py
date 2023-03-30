import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from src.utils import LoggingUtils
from torch.utils.tensorboard import SummaryWriter


def softmax(x, axis=1):
    """Compute softmax values for each sets of scores in x."""
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=axis, keepdims=True)

def softmax_torch(x, axis=1):
    """Compute softmax values for each sets of scores in x."""
    e_x = torch.exp(x - torch.max(x))
    return e_x / e_x.sum(axis=axis, keepdims=True)

class SoftmaxApprox(nn.Module):
    """
    Softmax approximation using linear network.
    """
    def __init__(self, relu=F.relu, hidden_size=64):
        """
        Initialize softmax approximation.
        Args:
            relu: relu function, `encrypted_support_relu` or `origin_relu`
            input_size: input size, should be equal with transformer `attention_size`
            hidden_size: hidden size
            output_size: output size (default == input_size)
        """
        super(SoftmaxApprox, self).__init__()
        self.relu = relu
        self.fc1 = nn.Linear(1, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, 1)


    def forward(self, input_tensor):
        """
        S(xi) = xi * T (∑_j ReLU(((xj)/2 + 1)^3))
        """
        e = self.relu((input_tensor / 2 + 1) ** 3)
        x = e.sum(dim=-1, keepdim=True).unsqueeze(-1)
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.fc3(x).squeeze(dim=-1)
        return e * x
    
    def origin_forward(self, input_tensor):
        t = input_tensor / 2 + 1
        exp_of_score = F.relu(t * t * t)
        x = exp_of_score.sum(-1, keepdim=True).unsqueeze(-1)
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.fc3(x).squeeze(dim=-1)
        return exp_of_score * x
    
class enc_softmax():
    def __init__(self, softmax_approx: SoftmaxApprox, relu=enc_relu):
        self.softmax_approx = softmax_approx
        # load weights
        self.fc1_weight = softmax_approx.fc1.weight.T.data.tolist()
        self.fc1_bias = softmax_approx.fc1.bias.data.tolist()
        self.fc2_weight = softmax_approx.fc2.weight.T.data.tolist()
        self.fc2_bias = softmax_approx.fc2.bias.data.tolist()
        self.fc2_weight = softmax_approx.fc2.weight.T.data.tolist()
        self.fc2_bias = softmax_approx.fc2.bias.data.tolist()

    def forward(self, enc_x):
        enc_x = enc_x / 2 + 1
        exp_score = self.enc_relu(enc_x * enc_x * enc_x)
        
        # fc1 layer
        enc_x = enc_x.mm(self.fc1_weight) + self.fc1_bias
        enc_x = self.relu(enc_x)
        # fc2 layer
        enc_x = enc_x.mm(self.fc2_weight) + self.fc2_bias

        return enc_x
    
        t = input_tensor / 2 + 1
        exp_of_score = F.relu(t * t * t)
        x = exp_of_score.sum(-1, keepdim=True).unsqueeze(-1)
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.fc3(x).squeeze(dim=-1)
        return exp_of_score * x
    

    
    def __call__(self, *args, **kwargs):
        return self.forward(*args, **kwargs)

class SoftmaxApproxTrainer():
    def __init__(self, softmodel: SoftmaxApprox, num_samples=1e6, input_size=128, batch_size=1, lr=0.0001, num_epochs=100):
        self.softmodel = softmodel
        self.num_samples = num_samples
        self.input_size = input_size
        self.batch_size = batch_size
        self.lr = lr
        self.num_epochs = num_epochs

    def _generate_train_data(self):
        """
        Generate training data for softmax approximation's linear network.
        """
        x = (torch.rand(self.num_samples, self.input_size) * 6) - 3
        x.requires_grad = False
        y = softmax_torch(x)
        y.requires_grad = False
        return x, y
    
    def train(self):
        x, y = self._generate_train_data()
        writer = SummaryWriter(log_dir='logs')
        loss = torch.nn.MSELoss()
        optimizer = torch.optim.Adam(self.softmodel.parameters(), lr=self.lr)

        for epoch in range(self.num_epochs):
            # TODO batch
            optimizer.zero_grad()
            l = loss(self.softmodel(x), y)
            l.sum().backward()
            optimizer.step()
            log.info(f'epoch {epoch + 1}, loss {float(l.sum()):.6f}')
            writer.add_scalar('loss', float(l.sum()), epoch)
        writer.close()

    def save(self, file_path="output/softmax_trained.model"):
        """
        Save model.
        """
        torch.save(self.softmodel.state_dict(), file_path)
        log.info(f"Model Saved on: {file_path}")
        return file_path

def test_appr_softmax():
    """
    test softmax approximation.
    """
    # forward test
    x = torch.randn(10)
    log.debug(f"x: {x}")
    softmax_appr = SoftmaxApprox()
    log.debug(f"softmax_appr: {softmax_appr(x)}")

    # train test
    softmax_appr_trainer = SoftmaxApproxTrainer(softmax_appr, num_samples=1000000, input_size=128)
    # log.debug(f"generate train data: {softmax_appr_trainer._generate_train_data()[0][0]}")
    softmax_appr_trainer.train()

def test_softmax():
    """
    Test softmax function.
    """
    x_torch = torch.rand(10, 10)
    x_np = x_torch.numpy()

    log.debug(f"torch: {x_torch[0][0]}")
    log.debug(f"numpy: {x_np[0][0]}")
 
    log.debug(f"softmax: {softmax(x_np)}")
    log.debug(f"softmax_torch: {softmax_torch(x_torch)}")


if __name__ == '__main__':
    log = LoggingUtils(logger_name='softmax_logger')
    log.add_console_handler()

    test_appr_softmax()
    # test_softmax()
