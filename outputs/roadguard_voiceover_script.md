# ROADGUARD AI — Official Explainer Video Narration Script

**Target Video:** `outputs/roadguard_explainer.mp4`  
**Duration:** 75 Seconds (01:15)  
**Pacing:** Confident, Authoritative, Tech-Forward, Clear (approx. 140 WPM)  
**Recommended AI Voice Persona:** Male or Female, Professional Deep Corporate Narrator (e.g., ElevenLabs *Adam* / *Daniel* / *Rachel*, or OpenAI TTS *Onyx* / *Alloy*)

---

## 🎙️ Synchronized Voiceover Script with Visual Cues

| Timestamp | Visual Cue on Screen | Narration Script (Exact Voice Lines) | Director Notes & Tone |
|:---|:---|:---|:---|
| **0:00 – 0:08** (8s) | Pulsing shield logo, neon brand title, and tagline reveal | *"Welcome to ROADGUARD AI — the next-generation smart-city platform for road damage intelligence and municipal maintenance triage."* | **Warm, Confident, Inspiring.** Clear emphasis on "ROADGUARD AI". Pause briefly after title. |
| **0:08 – 0:17** (9s) | 3 Problem cards slide in: $3.0B damage, 3-6 week delay, zero GIS data | *"Every year, billions of dollars are lost to road decay. Traditional inspections are slow, paper-bound, and leave hazardous potholes unattended."* | **Serious, Analytical.** Convey the severity of municipal road maintenance challenges. |
| **0:17 – 0:26** (9s) | 4-step pipeline flow cards illuminate: Capture ➔ Detect ➔ Score ➔ Dispatch | *"ROADGUARD AI transforms this into an automated, four-step intelligence pipeline: capture, detect, prioritize, and dispatch."* | **Dynamic, Energizing.** Emphasize the four sequential action verbs. |
| **0:26 – 0:38** (12s) | Road photo with scanning cyan laser line; Pothole (89%) and Crack (74%) bounding boxes appear | *"Powered by Ultralytics YOLO, our computer vision engine scans road imagery in real time, localizing potholes and structural fissures with high-confidence bounding box overlays and surface area metrics."* | **Tech-Focused, Precise.** Authoritative delivery on "Ultralytics YOLO" and "bounding box overlays". |
| **0:38 – 0:50** (12s) | Assessed hazard gauge counts to 88.5/100; 5-factor breakdown bars illuminate | *"Our explainable scoring engine calculates an objective 0 to 100 visual hazard index, factoring in damaged surface area, defect cluster density, and roadway traffic context."* | **Authoritative, Explainable.** Highlight that scoring is objective and mathematically sound. |
| **0:50 – 1:01** (11s) | Dark matter GIS map with pulsing Red, Amber, Green pins; incident popup preview | *"Every incident is mapped on an interactive GIS telemetry system with priority-coded markers, cluster analysis, and embedded photographic evidence."* | **Clear, Spatial.** Pacing matches the interactive map pin pulse. |
| **1:01 – 1:10** (9s) | Platform UI screenshot, ranked queue, and ReportLab PDF work order preview | *"Municipal authorities manage a live, ranked maintenance queue, audit repair lifecycles, and generate official civil engineering PDF work orders with a single click."* | **Executive, Pragmatic.** Confident tone focusing on authority empowerment and efficiency. |
| **1:10 – 1:15** (5s) | Final shield logo animation and `http://localhost:8501` CTA button | *"ROADGUARD AI: Building safer, smarter, data-driven municipal infrastructure."* | **Punchy, Inspiring.** Strong closing punchline with a crisp final cadence. |

---

## 🛠️ Recommended AI Speech Generation Settings

### 1. ElevenLabs (Recommended)
- **Voice:** *Adam* (Deep, Narrative) or *Daniel* (Authoritative British) or *Rachel* (Polished Corporate)
- **Model:** `Eleven Multilingual v2`
- **Stability:** `0.55`
- **Clarity / Similarity:** `0.85`
- **Style Exaggeration:** `0.15`
- **Speaker Boost:** `Enabled`

### 2. OpenAI Audio API (`tts-1-hd`)
- **Model:** `tts-1-hd`
- **Voice:** `onyx` (Deep & Professional) or `alloy` (Modern & Crisp)
- **Speed:** `1.02`

### 3. Microsoft Azure Speech / Edge TTS
- **Voice:** `en-US-AndrewMultilingualNeural` or `en-US-JennyNeural`
- **Rate:** `-2%` (0.98x)
- **Pitch:** `Default`
- **Format:** Audio file `outputs/voiceover_ssml.xml` can be pasted directly into Azure Speech Studio.
