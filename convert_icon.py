from PIL import Image
import os

def create_ico():
    png_path = os.path.join('src', 'assets', 'Logo.png')
    ico_path = os.path.join('src', 'assets', 'Logo.ico')
    
    if not os.path.exists(png_path):
        print(f"Error: {png_path} not found!")
        return
        
    # Open the PNG image
    img = Image.open(png_path)
    
    # Convert to RGBA if not already
    img = img.convert('RGBA')
    
    # Create ICO file
    # Windows recommends these sizes: 16, 32, 48, 64, 128, 256
    sizes = [(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)]
    img.save(ico_path, format='ICO', sizes=sizes)
    print(f"Created {ico_path}")

if __name__ == '__main__':
    create_ico() 