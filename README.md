# 💇‍♀️ Hair Color Matching Tool

A lightweight and intelligent system that allows users to upload a hair image and receive the closest matching product shade based on RGB analysis and Delta E distance metrics. Perfect for enhancing product recommendations in hair care and beauty platforms.

---

## 🚀 Features

-   Upload user hair photo
-   AI-powered hair segmentation to isolate hair from the background.
-   Extracts the average RGB color from the detected hair region.
-   Matches the user's hair color against a pre-processed dataset of product shades.
-   Calculates the Delta E (CIEDE2000) distance for perceptually accurate color comparison.
-   Returns detailed matching information: User's RGB, matched shade name, shade's RGB, and the Delta E value.
-   Customizable matching threshold to fine-tune results.
-   Ready for deployment and accessible via a REST API.

---

## 🛠️ Tech Stack

-   **Backend:** FastAPI
-   **AI/ML:** PyTorch
-   **Image Processing:** OpenCV, Pillow
-   **Color Science:** colormath for accurate color difference calculations.
-   **Data Handling:** JSON
-   **Deployment:** Render

---

## 📖 Getting Started

### Prerequisites

-   Python 3.8+
-   Git

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/Hair_Extension.git
    cd Hair_Extension
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For Windows
    python -m venv venv
    venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

To start the FastAPI server, run the following command from the project root directory:

```bash
uvicorn app.main:app --reload
```

The application will be available at `http://127.0.0.1:8000`.

---

## 🧪 How It Works

1.  A user uploads an image containing their hair.
2.  The **BiSeNet** deep learning model performs semantic segmentation to create a precise mask of the hair region.
3.  The average RGB color of the pixels within the hair mask is calculated.
4.  This average RGB value is converted to the LAB color space for a more perceptually uniform comparison.
5.  The system iterates through a pre-defined list of product shades, each with its own reference RGB value.
6.  The **Delta E (CIEDE2000)** is calculated between the user's hair color and each product shade.
7.  The shade with the lowest Delta E value is selected as the best match.
8.  The match details are returned to the user via the API.

---
## 📁 Project Structure
```
app/
├── routes/
│   └── hair_extension.py   # API endpoint logic
├── services/
│   ├── hair_color_detector.py # Hair segmentation and color extraction
│   ├── LabCoolor.py        # Utility for processing shade images
│   └── shade_matcher.py    # Core matching logic
├── utils/
│   └── color_matcher.py    # Color conversion and Delta E calculation
├── shade/
│   └── shade_rgb_signatures.json # Pre-processed shade data
├── config.py               # Application settings
├── main.py                 # FastAPI app entry point
├── model.py                # BiSeNet model definition
└── resnet.py               # ResNet backbone for BiSeNet

model/
└── model.pth               # Pre-trained BiSeNet model weights

data/                       # Raw images of hair extension shades
...

requirements.txt            # Project dependencies
```
---
## 🧠 The Model

This project uses a **BiSeNet (Bilateral Segmentation Network)** model for hair segmentation. The pre-trained weights are stored in `model/model.pth`. BiSeNet is efficient and accurate, making it ideal for distinguishing hair from complex backgrounds in user-submitted photos.

## 🎨 Shade Data

The `data/` directory contains the raw images used to create the shade reference file. Each subdirectory is named after a specific hair color shade and contains multiple images of that shade under different lighting conditions (e.g., natural light, indoor light, close-up).

The `app/services/LabCoolor.py` script processes these images to calculate an average RGB value for each shade, which is then stored in `app/shade/shade_rgb_signatures.json`.

---

## 📥 API Endpoint

**Endpoint:** `POST /hair/match-hair-color`

**Request:** `multipart/form-data`

-   **key**: `file`
-   **value**: The image file to be analyzed.

**Example with `curl`:**

```bash
curl -X POST "http://127.0.0.1:8000/hair/match-hair-color" -F "file=@/path/to/your/hair_image.jpg"
```

**Sample Response:**

```json
{
  "user_rgb": [112, 85, 74],
  "matched_shade": "Chocolate Brown",
  "shade_rgb": [107, 89, 79],
  "delta_e": 9.2
}
```

---

## 🌐 Deployment

The project is live and testable via the following Render-hosted link:

👉 **[https://hair-extension-dhfs.onrender.com/docs](https://hair-extension-dhfs.onrender.com/docs)**

Use the Swagger UI to test the `/hair/match-hair-color` endpoint directly from your browser.

<!-- ---

## 🔮 Future Improvements

-   **Automatic Hair Segmentation:** Integrate more advanced models like SAM (Segment Anything Model) for even more robust performance.
-   **AR Try-On:** Develop an augmented reality feature to let users preview hair extension shades live on their video feed.
-   **Admin Dashboard:** Create a simple web interface for uploading and managing hair shade data.
-   **Frontend Interface:** Build a user-friendly frontend for easier interaction.

--- -->

## 👩‍💻 Maintainers

**PromptNest Team**
Built with 💡 by:

-   [Roksana18cse04](https://github.com/Roksana18cse04)
-   [marziasu](https://github.com/marziasu)
-   [Hasib303](https://github.com/Hasib303)

*Expertise: Data Science, AI Engineering, Computer Vision, Full Stack Deployment*

---

<!-- ## 📌 Notes

-   Pull requests and contributions are welcome!
-   For Docker support, frontend integration, or batch testing utilities, please check future branches or reach out to the maintainers. -->