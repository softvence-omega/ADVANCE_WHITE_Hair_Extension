
# 💇‍♀️ Hair Color Matching Tool

A lightweight and intelligent system that allows users to upload a hair image and receive the closest matching product shade based on RGB analysis and Delta E distance metrics. Perfect for enhancing product recommendations in hair care and beauty platforms.

---

## 🚀 Features

- Upload user hair photo
- Manual or AI-based hair region selection
- Extracts average RGB from selected hair section
- Matches against a pre-processed shade RGB dataset
- Calculates Delta E (CIE76) for best match
- Returns match info: User RGB, Shade Name, Shade RGB, Delta E
- Customizable matching threshold
- Render-hosted and API-ready

---

## 🛠️ Tech Stack

- **Backend:** FastAPI  
- **Image Processing:** OpenCV, Pillow  
- **Color Matching:** LAB color space, Delta E (CIE76)  
- **Data Handling:** JSON-based shade storage  
- **Deployment:** Render

---

## 🧪 How It Works (Step-by-Step)

1. User uploads a hair image.
2. Hair region is manually selected (automation with segmentation coming soon).
3. Average RGB is extracted from that region.
4. Each product shade's RGB (pre-averaged from 3 lighting images) is compared.
5. Delta E is calculated between user RGB and shade RGB.
6. The closest matching shade (Delta E < 12) is returned.

---

## 📦 Shade Data Format

```json
[
  {
    "shade_name": "Chocolate Brown",
    "rgb": [107, 89, 79]
  }
]
````

Each shade is built from an average of 3 photos under different lighting conditions.

---

## 📥 API Endpoint

**Endpoint:** `POST /match-hair-color`

**Request:**

* `multipart/form-data`: UploadFile (image)

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

## 📈 Matching Threshold

* Default: `Delta E < 12`
* Fully configurable for tighter or looser matching

---

## 🔮 Future Improvements

* image previe option
* AR-based live preview of shades
* Admin dashboard to upload/edit shade sets
* User-facing UI for live image testing

---

## 📁 Project Structure

```
app/
├── routes/
│   └── hair_extension.py
├── services/
│   ├── hair_color_detector.py
│   ├── labcolor.py
│   └── shade_matcher.py
├── utils/
│   └── color_matcher.py
├── shade/
│   └── shade_rgb_signatures.json
├── config.py
├── main.py
├── model.py

model/
└── model.pth
data/
.gitignore
requirements.txt
```

---

## 🌐 Deployment

The project is live and testable via the following Render-hosted link:

👉 **[https://hair-extension-dhfs.onrender.com/docs](https://hair-extension-dhfs.onrender.com/docs)**

Use Swagger UI to test the `/match-hair-color` endpoint directly from the browser.

---

## 👩‍💻 Maintainers

**PromptNest Team**
Built with 💡 by:

* [Roksana18cse04](https://github.com/Roksana18cse04)
* [marziasu](https://github.com/marziasu)
* [Hasib303](https://github.com/Hasib303)

Expertise: Data Science, AI Engineering, Computer Vision, Full Stack Deployment

---

## 📌 Notes

* For Docker, frontend integration, or batch testing utilities, please reach out or check future branches.
* Pull requests and contributions are welcome!

---

