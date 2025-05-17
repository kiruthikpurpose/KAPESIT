import torch
from transformers import AutoModel, AutoTokenizer
from PIL import Image
import torchvision.transforms as T
import torchaudio

class TextPerception:
    def __init__(self, model_name='bert-base-uncased'):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
    def perceive(self, text):
        inputs = self.tokenizer(text, return_tensors='pt', truncation=True, padding=True)
        return self.model(**inputs).last_hidden_state

class ImagePerception:
    def __init__(self, model_name='resnet18'):
        import torchvision.models as models
        self.model = getattr(models, model_name)(pretrained=True)
        self.model.eval()
        self.transform = T.Compose([
            T.Resize((224, 224)),
            T.ToTensor(),
            T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
    def perceive(self, image_path):
        img = Image.open(image_path).convert('RGB')
        tensor = self.transform(img).unsqueeze(0)
        with torch.no_grad():
            return self.model(tensor)

class AudioPerception:
    def __init__(self):
        self.transform = torchaudio.transforms.MelSpectrogram()
    def perceive(self, audio_path):
        waveform, sr = torchaudio.load(audio_path)
        return self.transform(waveform) 