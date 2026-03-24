const recordBtn = document.getElementById('recordBtn');
const responseAudio = document.getElementById('responseAudio');

recordBtn.onclick = async () => {
    try {
        // 1️⃣ Request mic
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        let audioChunks = [];

        mediaRecorder.ondataavailable = e => audioChunks.push(e.data);

        mediaRecorder.onstop = async () => {
            // 2️⃣ Create audio file to send
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            const formData = new FormData();
            formData.append('file', audioBlob, 'user_audio.wav');

            // 3️⃣ Send to Flask
            const response = await fetch('/process_audio', { method: 'POST', body: formData });
            const audioUrl = await response.text();

            // 4️⃣ Play response
            responseAudio.src = audioUrl;
            responseAudio.play();
        };

        // 5️⃣ Start recording 5 seconds
        mediaRecorder.start();
        setTimeout(() => mediaRecorder.stop(), 5000);
    } catch (err) {
        alert("Error accessing microphone: " + err);
    }
};