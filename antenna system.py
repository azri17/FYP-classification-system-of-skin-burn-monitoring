import csv
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import numpy as np

# Define the full path to the image files
image_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the Python script
skinburn1_path = os.path.join(image_dir, "skinburn1.png")
skinburn2_path = os.path.join(image_dir, "skinburn2.png")
healthyskin_path = os.path.join(image_dir, "healthyskin.png")
skinburn3_path = os.path.join(image_dir, "skinburn3.png")
skinburn4_path = os.path.join(image_dir, "skinburn4.png")

# Information texts for each stage
info_texts = {
    "Burn Stage 1": "Stage 1 burns, also known as superficial burns or first-degree burns, affect only the outermost layer of the skin, the epidermis. These burns are typically caused by brief exposure to heat, such as a minor sunburn or a quick touch to a hot surface. The hallmark symptoms include redness, mild swelling, and pain. The skin might be tender to the touch, but there are no blisters or open wounds. These burns usually heal within a week, often without scarring, provided proper care is taken to keep the area clean and moisturized.\n\n First-degree burns are generally considered minor and can often be treated at home. Treatment includes cooling the burn with running cool water for several minutes, applying soothing lotions or aloe vera, and taking over-the-counter pain relief if necessary. It is important to avoid using ice, as it can damage the skin further. Keeping the burn protected from further sun exposure is also crucial to prevent aggravation and promote healing ",
    "Burn Stage 2": "Stage 2 burns, or partial thickness burns, penetrate deeper into the skin, affecting both the epidermis and part of the dermis. These burns are more severe than first-degree burns and can result from longer exposure to heat sources, scalding liquids, or more intense sunburns. Symptoms include blistering, intense redness, swelling, and significant pain. The blisters may break, revealing a moist, red, and weeping wound underneath.\n\n Healing time for second-degree burns can range from two to three weeks, depending on the severity and depth of the burn. Treatment typically involves cleaning the burn, applying antibiotic ointments, and covering it with a sterile, non-stick bandage to protect against infection. Medical attention might be required to properly manage pain, ensure proper wound care, and monitor for potential complications like infections. Some second-degree burns can cause scarring or changes in skin color, especially if not treated appropriately.",
    "Burn Stage 3": "Stage 3 burns, also known as full thickness burns or third-degree burns, extend through the entire dermis and affect deeper tissues. These burns can be caused by prolonged exposure to flames, hot liquids, or chemical and electrical sources. They are characterized by a leathery texture and a range of colors, from white to dark brown or black. Surprisingly, third-degree burns might not be painful initially due to nerve damage in the affected area, which can make them particularly dangerous.\n\n Healing from third-degree burns is complex and typically requires professional medical intervention. Since the skin’s regenerative layer is destroyed, these burns often necessitate surgical procedures such as skin grafting, where healthy skin from another part of the body is transplanted to the burn site. Long-term care includes managing potential complications like infections, extensive physical therapy to restore function and mobility, and cosmetic or reconstructive surgeries to address scarring and deformities.",
    "Burn Stage 4": "Stage 4 burns, or deep full thickness burns, are the most severe form of burns, extending beyond the skin and affecting underlying tissues such as muscles, tendons, and bones. These burns are usually caused by prolonged exposure to high-intensity heat, chemicals, or electricity. The affected area might appear charred, and there is a high risk of complications, including severe infections, significant fluid loss, and shock. The injury can be life-threatening and often requires immediate and intensive medical treatment.\n\n The treatment for fourth-degree burns is extensive and involves multiple stages. Initial care focuses on stabilizing the patient, preventing infection, and managing pain. This is followed by surgical interventions, including debridement (removal of dead tissue) and multiple skin grafts or flap surgeries to close the wounds. Long-term rehabilitation is crucial and involves physical therapy to regain mobility and function, as well as psychological support to cope with the trauma and potential changes in appearance. Recovery from fourth-degree burns is prolonged and can lead to permanent disability or disfigurement, requiring ongoing medical and supportive care.",
    "Error": "Error in classification."
}

def classify_stage(bandwidth):
    if 0.00 <= bandwidth <= 0.018:
        return "Healthy skin", healthyskin_path
    elif  0.019<= bandwidth <= 0.039:
        return "Burn Stage 1", skinburn1_path
    elif 0.040 <= bandwidth <= 0.099:
        return "Burn Stage 2", skinburn2_path
    elif 0.100 <= bandwidth <= 0.129:
        return "Burn Stage 3", skinburn3_path
    elif 0.130 <= bandwidth <= 0.200:
        return "Burn Stage 4", skinburn4_path
    else:
        return "Error", None

def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        process_csv(file_path)

def process_csv(file_path):
    min_magnitude = float('inf')
    min_freq = 0
    threshold = -10.0
    frequencies = []
    magnitudes = []

    with open(file_path, 'r') as file:
        for _ in range(3):
            next(file)
        reader = csv.reader(file, delimiter='\t')
        for row in reader:
            values = row[0].split('\t')
            freq = float(values[0].strip('"'))
            S11_magnitude = float(values[1].strip('"'))
            frequencies.append(freq)
            magnitudes.append(S11_magnitude)
            if S11_magnitude < min_magnitude:
                min_magnitude = S11_magnitude
                min_freq = freq

    cross_points = []
    for i in range(1, len(magnitudes)):
        if (magnitudes[i-1] - threshold) * (magnitudes[i] - threshold) < 0:
            f1, f2 = frequencies[i-1], frequencies[i]
            m1, m2 = magnitudes[i-1], magnitudes[i]
            cross_freq = f1 + (threshold - m1) * (f2 - f1) / (m2 - m1)
            cross_points.append(cross_freq)
            print(f"Cross point found: {cross_freq} GHz")

    # Find the two crossing points closest to the resonant frequency
    if len(cross_points) >= 2:
        cross_points = sorted(cross_points, key=lambda x: abs(x - min_freq))
        closest_cross_points = cross_points[:2]
        bandwidth = max(closest_cross_points) - min(closest_cross_points)
    else:
        bandwidth = 0

    print(f"Cross points: {cross_points}")
    print(f"Calculated bandwidth: {bandwidth} GHz")

    frequency = "{:.2f}".format(min_freq)
    magnitude = "{:.2f}".format(min_magnitude)
    bandwidth_str = "{:.3f}".format(bandwidth)

    stage, image_path = classify_stage(float(bandwidth))

    result_text = (f"Frequency at Minimum S11 Magnitude: {frequency} GHz\n"
                   f"Minimum S11 Magnitude: {magnitude} dB\n"
                   f"Bandwidth: {bandwidth_str} GHz\n"
                   f"Classification: {stage}\n")

    result_window = tk.Toplevel(root)
    result_window.title("Result")
    result_label = tk.Label(result_window, text=result_text, font=("Arial", 12))
    result_label.pack(padx=40, pady=40)
    
    #render,resize image
    load = Image.open(image_path)
    ori_image = load.resize((300, 300), Image.Resampling.LANCZOS)
    render = ImageTk.PhotoImage(ori_image)
    img_label = tk.Label(result_window, image=render)
    img_label.image = render
    img_label.pack(padx=10, pady=8)

#info_button
    info_button_text_label = tk.Label(result_window, text="To get more info, click INFO button", font=("Arial", 10))
    info_button_text_label.pack(pady=5) 
    info_button = tk.Button(result_window, text="INFO", command=lambda: show_info(stage), font=("Arial", 12, "bold"), bg="#B8E2F2")
    info_button.pack(pady=10)

#classify another file button
    another_file_text_label = tk.Label(result_window, text="To classify again, click button below", font=("Arial", 10))
    another_file_text_label.pack(pady=5)
    another_file_button = tk.Button(result_window, text="Classify Another File", command=browse_file, font=("Arial", 10))
    another_file_button.pack(pady=10)

#info window
def show_info(stage):
    info_window = tk.Toplevel(root)
    info_window.title("Info")

    info_text = info_texts.get(stage, "No information available.")

    text_widget = tk.Text(info_window, wrap="word", font=("Arial", 12), padx=10, pady=10)
    text_widget.insert(tk.END, info_text)
    text_widget.config(state=tk.DISABLED)

    scrollbar = tk.Scrollbar(info_window, command=text_widget.yview)
    text_widget.config(yscrollcommand=scrollbar.set)

    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# GUI setup
root = tk.Tk()
root.title("Skin Burn Classification")

root.geometry("400x400")
root.configure(bg="#f0f0f0")

label = tk.Label(root, text="Select CSV File:", bg="#f0f0f0", font=("Arial", 12))
label.pack(pady=10)

browse_button = tk.Button(root, text="Browse", command=browse_file, font=("Arial", 10))
browse_button.pack()

root.mainloop()
