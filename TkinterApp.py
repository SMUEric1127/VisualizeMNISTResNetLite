from tkinter import *
from PIL import Image, ImageTk, ImageGrab, ImageOps
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras import Model
from PIL import ImageGrab
import numpy as np
import matplotlib.pyplot as plt
import threading
import cv2
import asyncio
app = Tk()
app.geometry("150x150")

a = 10

model = load_model("LiteResnet.h5")
def get_x_and_y(event):
    global lasx, lasy
    lasx, lasy = event.x, event.y

def draw_smth(event):
    global lasx, lasy
    canvas.create_line((lasx, lasy, event.x, event.y), fill='white', width=3)
    lasx, lasy = event.x, event.y

async def graphGen():
    global layers
    imgnp = getImage()
    layer_outputs = [layer.output for layer in model.layers[1:]]

    visualize_model = Model(inputs = model.input, outputs = layer_outputs)
    
    layer_names = [layer.name for layer in model.layers]
    feature_maps = visualize_model.predict(imgnp.reshape((1,28,28,1)))

    #0 4 8 11
    layers = [feature_maps[0], feature_maps[1], feature_maps[4], feature_maps[5], feature_maps[8], feature_maps[9], feature_maps[11]]
    layer_names = [layer_names[0], layer_names[1], layer_names[4], layer_names[5], layer_names[8], layer_names[9], layer_names[11]]

    layers = [feature_maps[:11]]
    layer_names = [layer_names[:11]]

    sizeC = 20
    noLayers = 11
    f, axs = plt.subplots(sizeC, noLayers, figsize=(15,15))
    for j in range(noLayers):
        myLayer = np.array(layers[0][j][0])
        for i in range(sizeC):
            x = myLayer[:, :, i]
            x -= x.mean()
            x /= x.std()
            x *= 64
            x += 128
            x = np.clip(x, 0, 255).astype('uint8')
            ax = axs[i, j]
            ax.imshow(x, cmap='plasma')
            # Turn off tick labels
            ax.set_yticklabels([])
            ax.set_xticklabels([])
    f.savefig("test.png")
    img = cv2.imread("test.png")
    img = remove_background(img)
    img = cv2.resize(img, (600, 600))
    cv2.imwrite("test.png", img)
    print("SAVED")

def getImage():
    x=app.winfo_rootx()+canvas.winfo_x()
    y=app.winfo_rooty()+canvas.winfo_y()
    x1=x+canvas.winfo_width()
    y1=y+canvas.winfo_height()
    img = ImageGrab.grab().crop((x + a,y + a,x1 - a,y1 - a))
    img.save("ok.png")
    img = ImageOps.grayscale(img)
    img = img.resize((28,28))
    imgnp = np.array(img).reshape((1, 28, 28, 1))
    return imgnp/255

async def getter():
    global info, myImage, label, pred
    try:
        info.quit()
    except:
        print("not init")
    info = Tk()
    info.geometry("700x650")
    global imgnp, prediction
    pred  = model.predict(getImage())
    prediction = np.argmax(pred)

    await graphGen()

    myImage = PhotoImage(master=info, file="test.png")
    predLabel = Label(info, text=f"predicted: {prediction} - softmax: {pred[0][prediction]*100}% ")
    predLabel.pack(side=TOP)
    label = Label(info, image=myImage)
    label.pack(anchor='center')

    canvas.delete("all")

def buttonClick():
    asyncio.run( getter())

def remove_background(image, bg_color=255):
    # assumes rgb image (w, h, c)
    intensity_img = np.mean(image, axis=2)

    # identify indices of non-background rows and columns, then look for min/max indices
    non_bg_rows = np.nonzero(np.mean(intensity_img, axis=1) != bg_color)
    non_bg_cols = np.nonzero(np.mean(intensity_img, axis=0) != bg_color)
    r1, r2 = np.min(non_bg_rows), np.max(non_bg_rows)
    c1, c2 = np.min(non_bg_cols), np.max(non_bg_cols)

    # return cropped image
    return image[r1:r2+1, c1:c2+1, :]

def saveFig():
    f = graphGen()
    f.savefig("ok.png")

def predict():
    try:
        info.quit()
    except:
        print("Not init")
    pred  = model.predict(getImage())
    prediction = np.argmax(pred)
    print(f"predicted: {prediction} - softmax: {pred[0][prediction]*100}%)")
    canvas.delete("all")
    
    
predictButton = Button(app, text="Plot", fg="black", command = buttonClick)
predictButton.pack(anchor='n')

reset = Button(app, text="Predict", fg="black", command = predict)
reset.pack(anchor='n')

canvas = Canvas(app, bg='black', width=128, height=128)
canvas.pack(anchor='center', expand=1)

canvas.bind("<Button-1>", get_x_and_y)
canvas.bind("<B1-Motion>", draw_smth)
