// frontend/interview.js

// --- DOM Elements ---
const statusEl = document.getElementById('status');
const webcamEl = document.getElementById('webcam');
const indicatorEl = document.getElementById('indicator');
const welcomeUI = document.getElementById('welcome-ui');
const interviewUI = document.getElementById('interview-ui');
const startBtn = document.getElementById('start-interview-btn');
const timerDisplay = document.getElementById('timer-display');
const overlayCanvas = document.getElementById('overlay');

// ✅ NEW DOM elements (Verification + Proctoring warnings)
const idCardInput = document.getElementById("id-card-input");
const captureWebcamEl = document.getElementById("capture-webcam");
const capturePhotoBtn = document.getElementById("capture-photo-btn");
const uploadVerificationBtn = document.getElementById("upload-verification-btn");
const capturedPhotoPreview = document.getElementById("captured-photo-preview");
const verificationStatusEl = document.getElementById("verification-status");

const warningBox = document.getElementById("warning-box");
const warningTextEl = document.getElementById("warning-text");
const warningCountEl = document.getElementById("warning-count");

// --- State Variables ---
const interviewId = new URLSearchParams(window.location.search).get('interview_id');

// ✅ NEW DOM element for enabling camera manually
const enableCameraBtn = document.getElementById("enable-camera-btn");

let mediaRecorder;
let audioChunks = [];
let socket;
let proctoringInterval;
let interviewTimer;
let isDetecting = false;
let timerStarted = false;


// ✅ NEW proctoring state
let warnings = 0;
let violations = 0;
const VIOLATIONS_PER_WARNING = 50;   // e.g., every 15 violations = 1 warning
const MAX_WARNINGS = 3;
let lastPopupShownAtWarning = 0;
let verificationUploaded = false;
let capturedPhotoBlob = null;
let captureStream = null;

// ✅ API base URL
// IMPORTANT: Use same port as your FastAPI backend
const API_BASE = "https://mac-interlunar-nonancestrally.ngrok-free.dev";

// --- Event Listeners ---
startBtn.addEventListener('click', initializeInterview);
capturePhotoBtn.addEventListener("click", captureCandidatePhoto);
uploadVerificationBtn.addEventListener("click", uploadVerificationData);
idCardInput.addEventListener("change", onIdCardSelected);

// ✅ NEW: Enable Camera button click
enableCameraBtn.addEventListener("click", startVerificationWebcam);

// --- Initial Setup on Page Load ---
window.addEventListener("load", () => {
    // Disable start button until verification done
    startBtn.disabled = true;

    // Disable upload button until both ID + photo ready
    uploadVerificationBtn.disabled = true;

    // Camera will NOT start automatically now
    verificationStatusEl.textContent = "Click 'Enable Camera' to start verification.";
});


// ✅ Verification Webcam Startup (Now user-triggered)
async function startVerificationWebcam() {
    try {
        verificationStatusEl.textContent = "Requesting camera permission...";
        enableCameraBtn.disabled = true;

        captureStream = await navigator.mediaDevices.getUserMedia({
            video: true,
            audio: false
        });

        captureWebcamEl.srcObject = captureStream;

        captureWebcamEl.onloadedmetadata = () => {
            captureWebcamEl.play();
        };

        verificationStatusEl.textContent = "✅ Camera enabled. Now upload your ID and capture your photo.";
    } catch (err) {
        console.error("Verification webcam error:", err);

        let msg = "❌ Camera permission denied. Please allow permission and try again.";
        if (err.name === "NotAllowedError") {
            msg = "❌ Camera permission denied. Please allow camera permission from browser settings.";
        } else if (err.name === "NotFoundError") {
            msg = "❌ No camera device found on this system.";
        } else if (err.name === "NotReadableError") {
            msg = "❌ Camera is already being used by another application (Zoom / Teams / Meet).";
        }

        verificationStatusEl.textContent = msg;
        enableCameraBtn.disabled = false;
        startBtn.disabled = true;
    }
}

// ✅ When ID selected
function onIdCardSelected() {
    if (!idCardInput.files || idCardInput.files.length === 0) {
        uploadVerificationBtn.disabled = true;
        return;
    }
    uploadVerificationBtn.disabled = !capturedPhotoBlob;
}

// ✅ Capture candidate photo from webcam preview
function captureCandidatePhoto() {
    if (!captureWebcamEl.srcObject) {
        verificationStatusEl.textContent = "❌ Camera is OFF. Please click 'Enable Camera' first.";
        return;
    }

    const canvas = document.createElement("canvas");
    canvas.width = captureWebcamEl.videoWidth || 640;
    canvas.height = captureWebcamEl.videoHeight || 480;

    const ctx = canvas.getContext("2d");
    ctx.translate(canvas.width, 0);
    ctx.scale(-1, 1);
    ctx.drawImage(captureWebcamEl, 0, 0, canvas.width, canvas.height);

    canvas.toBlob((blob) => {
        if (!blob) {
            verificationStatusEl.textContent = "❌ Failed to capture photo.";
            return;
        }

        capturedPhotoBlob = blob;

        // show preview image
        const imgUrl = URL.createObjectURL(blob);
        capturedPhotoPreview.src = imgUrl;
        capturedPhotoPreview.style.display = "block";
        captureWebcamEl.style.display = "none";

        // ✅ TURN OFF CAMERA after capture
        stopVerificationCamera();

        verificationStatusEl.textContent = "✅ Photo captured. Camera is now turned off. Upload verification.";
        uploadVerificationBtn.disabled = !(idCardInput.files && idCardInput.files.length > 0);

    }, "image/jpeg", 0.95);
}


// ✅ Stop verification webcam
function stopVerificationCamera() {
    if (captureWebcamEl && captureWebcamEl.srcObject) {
        captureWebcamEl.srcObject.getTracks().forEach(track => track.stop());
        captureWebcamEl.srcObject = null;
    }
}


async function captureSilentSnapshot() {
    try {
        if (!webcamEl || !webcamEl.srcObject) return;

        const canvas = document.createElement("canvas");
        canvas.width = webcamEl.videoWidth || 640;
        canvas.height = webcamEl.videoHeight || 480;

        const ctx = canvas.getContext("2d");

        // Mirror effect like camera preview
        ctx.translate(canvas.width, 0);
        ctx.scale(-1, 1);
        ctx.drawImage(webcamEl, 0, 0, canvas.width, canvas.height);

        const blob = await new Promise(resolve => canvas.toBlob(resolve, "image/jpeg", 0.85));
        if (!blob) return;

        const formData = new FormData();
        formData.append("snapshot", blob, `snapshot_${Date.now()}.jpg`);

        await fetch(`${API_BASE}/api/interviews/${interviewId}/snapshot`, {
            method: "POST",
            headers:{
                "ngrok-skip-browser-warning": "69420"
            },
            body: formData
        });

        // ❌ No UI update — silent
        console.log("✅ Silent snapshot saved");

    } catch (err) {
        console.warn("Silent snapshot failed:", err);
    }
}

async function uploadVerificationData() {
    if (!interviewId) {
        verificationStatusEl.textContent = "❌ Interview ID missing in URL.";
        return;
    }

    if (!idCardInput.files || idCardInput.files.length === 0) {
        verificationStatusEl.textContent = "❌ Please upload ID card photo.";
        return;
    }

    if (!capturedPhotoBlob) {
        verificationStatusEl.textContent = "❌ Please capture your photo.";
        return;
    }

    try {
        uploadVerificationBtn.disabled = true;
        verificationStatusEl.textContent = "Uploading verification... please wait.";

        const formData = new FormData();
        formData.append("id_card", idCardInput.files[0]);
        formData.append("candidate_photo", capturedPhotoBlob, "candidate_photo.jpg");

        const res = await fetch(`${API_BASE}/api/interviews/${interviewId}/verification`, {
            method: "POST",
            headers:{
                "ngrok-skip-browser-warning": "true" // ✅ Add this line
            },
            body: formData
        });

        const data = await res.json();

        if (!res.ok) {
            throw new Error(data.detail || "Verification upload failed");
        }

        verificationUploaded = true;
        verificationStatusEl.textContent = "✅ Verification uploaded successfully. You can start setup now.";
        startBtn.disabled = false;
        startBtn.textContent = "Start Setup";

    } catch (err) {
        console.error("Verification upload error:", err);
        verificationStatusEl.textContent = "❌ Upload failed: " + err.message;
        uploadVerificationBtn.disabled = false;
        startBtn.disabled = true;
    }
}




// --- Main Initialization Function ---
async function initializeInterview() {
    if (!verificationUploaded) {
        alert("Please complete identity verification (ID upload + photo capture) before starting the interview.");
        return;
    }

    startBtn.disabled = true;
    startBtn.textContent = "Setting up, please wait...";

    // 1. Setup camera and load AI proctoring models
    const stream = await setupCameraAndProctoring();

    if (stream) {
        // 2. Switch UI views
        welcomeUI.style.display = 'none';
        interviewUI.style.display = 'block';
        timerDisplay.style.display = 'inline-block';

        // 3. Connect WebSocket
        setupWebSocket(stream);
        // 4. Start silent snapshot interval
        startSilentSnapshots();

        // Start interview timer
        // startInterviewTimer(600);

        let snapshotInterval = null;
        function startSilentSnapshots(){
            //take first snapshot after 20 seconds
            setTimeout(() => {
                captureSilentSnapshot();
        }, 20000);

            //then take snapshots every 60 seconds
            snapshotInterval = setInterval(() => {
                captureSilentSnapshot();
            }, 90000);
        }

    } else {
        startBtn.disabled = false;
        startBtn.textContent = "Retry Setup";
    }
}

// --- Feature 1: Camera & AI Proctoring Setup ---
async function setupCameraAndProctoring() {
    try {
        statusEl.textContent = "Loading AI models...";

        await Promise.all([
            faceapi.nets.tinyFaceDetector.loadFromUri('models'),
            faceapi.nets.faceLandmark68Net.loadFromUri('models'),
            faceapi.nets.faceExpressionNet.loadFromUri('models')
        ]);

        statusEl.textContent = "Please grant camera and microphone access when prompted...";

        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        webcamEl.srcObject = stream;

        await new Promise(resolve => webcamEl.onloadedmetadata = resolve);

        indicatorEl.style.display = "none";

        // ✅ Start proctoring
        startProctoring();

        return stream;
    } catch (err) {
        console.error("Camera/Mic Error:", err.name, err.message);

        let userMessage = "An unknown error occurred while trying to access your camera.";
        if (err.name === "NotAllowedError" || err.name === "PermissionDeniedError") {
            userMessage = "Access to camera and microphone was denied. Please allow permissions and refresh.";
        } else if (err.name === "NotFoundError" || err.name === "DevicesNotFoundError") {
            userMessage = "No camera or microphone was found. Please connect them and try again.";
        } else if (err.name === "NotReadableError" || err.name === "TrackStartError") {
            userMessage = "Camera or microphone is already in use by another application. Close other apps and retry.";
        }

        alert("Error: " + userMessage);
        statusEl.textContent = userMessage;
        return null;
    }
}

// --- ✅ Feature 2: AI Proctoring Logic (Warnings + Auto Terminate) ---

function showWarning(message) {
    warnings += 1;

    warningBox.style.display = "block";
    warningTextEl.textContent = "⚠️ " + message;
    warningCountEl.textContent = `Warning ${warnings} / ${MAX_WARNINGS}`;

    // Send proctoring warning event to backend
    sendProctoringEvent("warning", message);

    if (warnings >= MAX_WARNINGS) {
        // terminate interview
        terminateInterviewDueToCheating(message);
    }
}

// async function sendProctoringEvent(eventType, message) {
//     try {
//         await fetch(`${API_BASE}/api/interviews/${interviewId}/proctoring-event`, {
//             method: "POST",
//             headers: { "Content-Type": "application/json" },
//             body: JSON.stringify({
//                 event_type: eventType,
//                 message: message,
//                 warnings: warnings,
//                 timestamp: new Date().toISOString()
//             })
//         });
//     } catch (err) {
//         console.warn("Failed to send proctoring event:", err);
//     }
// }


async function sendProctoringEvent(eventType, message) {
    try {
        await fetch(`${API_BASE}/api/interviews/${interviewId}/proctoring-event`, {
            method: "POST",
            headers: { 
                "Content-Type": "application/json",
                "ngrok-skip-browser-warning": "69420"
            },
            body: JSON.stringify({
                event_type: eventType,
                message: message,
                warnings: warnings,
                timestamp: new Date().toISOString()
            })
        });
    } catch (err) {
        console.warn("Failed to send proctoring event:", err);
    }
}



async function terminateInterviewDueToCheating(reason) {
    // update backend final status
    await sendProctoringEvent("cheating_detected", `Interview terminated: ${reason}`);

    statusEl.innerHTML = `<strong style="color:red;">Interview terminated due to suspicious activity.</strong><br/><br/>Reason: ${reason}`;

    stopEverything();

    // Close window after short delay
    setTimeout(() => {
        window.close();
    }, 2500);
}

// Show live hints on UI
function startProctoring() {
    const displaySize = {
        width: webcamEl.videoWidth || 640,
        height: webcamEl.videoHeight || 480
    };

    overlayCanvas.width = displaySize.width;
    overlayCanvas.height = displaySize.height;

    faceapi.matchDimensions(overlayCanvas, displaySize);

    proctoringInterval = setInterval(async () => {
        if (isDetecting || !webcamEl.srcObject) return;
        isDetecting = true;

        try {
            const detections = await faceapi
                .detectAllFaces(webcamEl, new faceapi.TinyFaceDetectorOptions())
                .withFaceLandmarks();

            const resizedDetections = faceapi.resizeResults(detections, displaySize);

            const ctx = overlayCanvas.getContext("2d");
            ctx.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);

            // ✅ Draw center guide lines (alignment help)
            ctx.strokeStyle = "rgba(0, 255, 255, 0.7)";
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(displaySize.width / 2, 0);
            ctx.lineTo(displaySize.width / 2, displaySize.height);
            ctx.stroke();

            ctx.beginPath();
            ctx.moveTo(0, displaySize.height / 2);
            ctx.lineTo(displaySize.width, displaySize.height / 2);
            ctx.stroke();

            // ✅ Draw face detections
            if (resizedDetections.length > 0) {
                faceapi.draw.drawDetections(overlayCanvas, resizedDetections);
                faceapi.draw.drawFaceLandmarks(overlayCanvas, resizedDetections);

                // ✅ Check posture alignment
                const box = resizedDetections[0].detection.box;
                const faceCenterX = box.x + box.width / 2;
                const faceCenterY = box.y + box.height / 2;

                const offsetX = Math.abs(faceCenterX - displaySize.width / 2);
                const offsetY = Math.abs(faceCenterY - displaySize.height / 2);

                // ✅ Show posture hints on UI
                if (offsetX > 120 || offsetY > 120) {
                    showLiveHint("⚠️ Please align your face in the center.");
                } else {
                    showLiveHint("✅ Face aligned properly.");
                }

            } else {
                showLiveHint("⚠️ Face not detected. Stay in front of the camera.");
                registerViolation("Face not detected. Please stay in front of the camera.");
            }

        } catch (err) {
            console.warn("Proctoring detection error:", err);
        } finally {
            isDetecting = false;
        }

    }, 1500);
}

// Trigger warning and log to backend
function registerViolation(reason) {
    violations++;

    // ✅ Every 15 violations => 1 warning
    if (violations % VIOLATIONS_PER_WARNING !== 0) {
        return; // ignore until reaching 15, 30, 45...
    }

    warnings++;
    showWarningUI(reason);

    // ✅ Popup only once per warning
    if (warnings > lastPopupShownAtWarning) {
        lastPopupShownAtWarning = warnings;
        showWarningPopup(reason);
    }

    // ✅ Terminate only after warning 5
    if (warnings >= MAX_WARNINGS) {
        terminateInterview(reason);
    }
}

// Show warning popup
function showWarningUI(reason) {
    warningBox.style.display = "block";
    warningBox.style.borderColor = "red";
    warningBox.style.background = "#ffe6e6";

    warningTextEl.textContent = `⚠️ ${reason}`;
    warningTextEl.style.color = "red";

    warningCountEl.textContent = warnings;
}

// Show warning popup dialog
function showWarningPopup(reason) {
    const popup = document.createElement("div");
    popup.style.position = "fixed";
    popup.style.top = "0";
    popup.style.left = "0";
    popup.style.width = "100%";
    popup.style.height = "100%";
    popup.style.background = "rgba(0,0,0,0.6)";
    popup.style.display = "flex";
    popup.style.alignItems = "center";
    popup.style.justifyContent = "center";
    popup.style.zIndex = "9999";

    popup.innerHTML = `
        <div style="
            background:white;
            padding:25px;
            border-radius:12px;
            max-width:450px;
            width:90%;
            box-shadow:0 0 20px rgba(0,0,0,0.4);
            text-align:center;
            font-family:Arial,sans-serif;
        ">
            <h2 style="color:red;margin-bottom:10px;">⚠️ Warning ${warnings}/${MAX_WARNINGS}</h2>
            <p style="font-size:16px;margin-bottom:20px;color:#111;">
                ${reason}
            </p>
            <button id="close-popup-btn" style="
                background:#ef4444;
                color:white;
                border:none;
                padding:10px 18px;
                border-radius:8px;
                font-size:15px;
                cursor:pointer;
            ">
                OK
            </button>
        </div>
    `;

    document.body.appendChild(popup);

    document.getElementById("close-popup-btn").onclick = () => {
        popup.remove();
    };

    // ✅ Auto close after 4 seconds also
    setTimeout(() => {
        if (document.body.contains(popup)) popup.remove();
    }, 4000);
}


// show the live hint msg on the UI
function showLiveHint(message) {
    // Shows guidance message without warning count
    if (warningTextEl) {
        warningTextEl.textContent = message;
        warningBox.style.display = "block";
        warningBox.style.borderColor = "#2563eb";
        warningBox.style.background = "#eff6ff";
        warningTextEl.style.color = "#1d4ed8";
    }
}


function avgX(points) {
    if (!points || points.length === 0) return 0;
    let sum = 0;
    for (const p of points) sum += p.x;
    return sum / points.length;
}

// --- Feature 3: Interview Timer ---
function startInterviewTimer(duration) {
    let timer = duration;
    interviewTimer = setInterval(() => {
        let minutes = parseInt(timer / 60, 10);
        let seconds = parseInt(timer % 60, 10);

        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        timerDisplay.textContent = minutes + ":" + seconds;

        if (--timer < 0) {
            clearInterval(interviewTimer);
            statusEl.textContent = "Time is up! Finalizing interview...";
            if (socket && socket.readyState === WebSocket.OPEN) socket.close();
        }
    }, 1000);
}



// --- WebSocket & Recording Logic ---
function setupWebSocket(stream) {
    let hasError = false;
    const socketUrl = `wss://mac-interlunar-nonancestrally.ngrok-free.dev/ws/interview/${interviewId}`;

    socket = new WebSocket(socketUrl);

    socket.onopen = () => statusEl.textContent = "Connection established. The interview will begin shortly.";

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === "error") {
            hasError = true;
        }
        handleServerMessage(data, stream);
    };

    socket.onclose = () => {
        if (!hasError) {
             statusEl.textContent = "Interview session has ended. You may now close this window.";
        }
        stopEverything();
    };

    socket.onerror = () => {
        if (!hasError) {
             statusEl.textContent = "A connection error occurred. Please refresh the page.";
        }
        stopEverything();
    };
}






// Handle messages from server
function handleServerMessage(data, stream) {
    statusEl.innerHTML = `<strong>AI:</strong> ${data.text}`;

    // ✅ Start timer only ONCE when first real question arrives
    if (!timerStarted && data.type === "question") {
        timerStarted = true;
        startInterviewTimer(600);  // 10 minutes
        console.log("✅ Timer started (10 mins)");
    }

    switch (data.type) {
        case "question":
        case "status":
            const utterance = new SpeechSynthesisUtterance(data.text);
            window.speechSynthesis.speak(utterance);
            utterance.onend = () => {
                if (data.type === "question") startRecording(stream);
            };
            break;

        case "thank_you":
            const thankYouUtterance = new SpeechSynthesisUtterance(data.text);
            window.speechSynthesis.speak(thankYouUtterance);
            thankYouUtterance.onend = () => {
                setTimeout(() => {
                    if (socket && socket.readyState === WebSocket.OPEN) socket.close();
                }, 4000);
            };
            break;

        case "error":
            statusEl.innerHTML = `<strong style="color:red;">Error: ${data.text}</strong>`;
            stopEverything();
            break;

        case "complete":
            stopEverything();
            break;
    }
}

// Record audio answer and send to backend
function startRecording(stream) {
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];

    mediaRecorder.ondataavailable = event => audioChunks.push(event.data);

    mediaRecorder.onstart = () => {
        statusEl.textContent = "Listening for your answer...";
        indicatorEl.style.display = 'block';
    };

    mediaRecorder.onstop = async () => {
        indicatorEl.style.display = 'none';

        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });

        if (socket && socket.readyState === WebSocket.OPEN) {
            try {
                const buffer = await audioBlob.arrayBuffer();   // ✅ Convert Blob -> Bytes
                socket.send(buffer);                            // ✅ Send bytes properly
                statusEl.textContent = "Answer sent. Please wait for the next question...";
            } catch (err) {
                console.error("Failed to send audio:", err);
                statusEl.textContent = "Error sending audio. Please retry...";
            }
        }
    };

    mediaRecorder.start();

    setTimeout(() => {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            mediaRecorder.stop();
        }
    }, 30000);
}


// --- Cleanup Function ---
function stopEverything() {
    window.speechSynthesis.cancel();

    // stop interview webcam
    if (webcamEl.srcObject) {
        webcamEl.srcObject.getTracks().forEach(track => track.stop());
        webcamEl.srcObject = null;
    }

    // stop verification webcam
    if (captureWebcamEl && captureWebcamEl.srcObject) {
        captureWebcamEl.srcObject.getTracks().forEach(track => track.stop());
        captureWebcamEl.srcObject = null;
    }

    if (proctoringInterval) clearInterval(proctoringInterval);
    if (interviewTimer) clearInterval(interviewTimer);

    if (mediaRecorder && mediaRecorder.state === 'recording') mediaRecorder.stop();
    if (snapshotInterval) clearInterval(snapshotInterval);

}

// --- WebSocket Event Handlers ---
socket.onopen = () => {
    console.log("✅ WebSocket OPEN");
    statusEl.textContent = "Connected. Waiting for first question...";
};

socket.onclose = (e) => {
    console.log("❌ WebSocket CLOSED", e.code, e.reason);
    statusEl.textContent = "Interview session has ended. You may now close this window.";
    stopEverything();
};

socket.onerror = (e) => {
    console.log("❌ WebSocket ERROR", e);
};
