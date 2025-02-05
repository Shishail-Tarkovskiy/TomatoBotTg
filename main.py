import cv2
import timm
import torch
import torch.nn as nn
import torch.nn.functional as F
import albumentations as A
import albumentations.pytorch as AP
from albumentations import (Compose)
import telebot

token = '7223315998:AAGryp3B4y9OoADvPZZAZXCEFPm2wv84JlY'

class MyMobileV3Net(torch.nn.Module):
    def __init__(self, model_name='mobilenetv3_large_100', pretrained=False):
        super().__init__()
        self.model = timm.create_model(model_name, pretrained=pretrained)

        self.model.classifier = torch.nn.Sequential(
          torch.nn.Linear(1280, 512),
          torch.nn.ReLU(),
          torch.nn.Linear(512, 7),
        )

    def forward(self, x):
        x = self.model(x)
        return x

class_names = ['Bacterial_spot', 'Black_mold', 'Early_blight', 'Healthy', 'Late_blight', 'Mosaic_virus', 'Septoria_spot']

pred_transforms = Compose([
    A.Resize(224, 224),
    A.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    ),
    AP.ToTensorV2()])

device = torch.device('cpu')
model = MyMobileV3Net('mobilenetv3_large_100', pretrained=False)

def predict_image(image):
    image_tensor = pred_transforms(image=image)["image"].unsqueeze(0)
    image_tensor = image_tensor.clone().detach()
    input = image_tensor.to(device)
    outputs = model(input)
    _, preds = torch.max(outputs, 1)
    prob = F.softmax(outputs, dim=1)
    top_p, top_class = prob.topk(1, dim=1)
    result = class_names[int(preds.cpu().numpy())]
    return result

bot = telebot.TeleBot(token)

@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.send_message(message.chat.id, "Привет! Отправь мне фото, и я его классифицирую.")

@bot.message_handler(content_types=["photo"])
def photo(message):
    print('message.photo =', message.photo)
    fileID = message.photo[-1].file_id
    print('fileID =', fileID)
    file_info = bot.get_file(fileID)
    print('file.file_path =', file_info.file_path)
    downloaded_file = bot.download_file(file_info.file_path)

    with open("image.jpg", 'wb') as new_file:
        new_file.write(downloaded_file)

    image = cv2.imread("image.jpg")
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    prediction = predict_image(image)

    bot.send_message(message.chat.id, 'Classified as: ' + prediction)
    print('classified as: ' + prediction)
    print('waiting for message...')

def main():
    model.load_state_dict(torch.load('model/mobilenetv3_large_100_best.pth', map_location=torch.device('cpu')))
    model.eval()
    model.to(device)
    print('waiting for message...')
    bot.polling(none_stop=True)

if __name__ == "__main__":
    main()