const MOOD_COLORS = {
  Surprise: { primary: '#c45c8a', light: '#d97aaa', dark: '#8a3060', text: '#ffffff' },
  Fear:     { primary: '#7260b0', light: '#9880cc', dark: '#4a3a80', text: '#ffffff' },
  Disgust:  { primary: '#3d8060', light: '#5aa07a', dark: '#225040', text: '#ffffff' },
  Happy:    { primary: '#ffdb77', light: '#e8c860', dark: '#deb358', text: '#2B1F1D' },
  Sad:      { primary: '#4470b0', light: '#6a90cc', dark: '#284880', text: '#ffffff' },
  Angry:    { primary: '#b04848', light: '#cc6a6a', dark: '#802828', text: '#ffffff' },
  Neutral:  { primary: '#8a7a72', light: '#b0a49e', dark: '#5c4f4a', text: '#ffffff' },
};

const MOOD_EMOJI_TEXT = {
  Surprise: '(o_O)',
  Fear:     '(>_<)',
  Disgust:  '(-_-)',
  Happy:    '(^_^)',
  Sad:      '(T_T)',
  Angry:    '(>_<)!',
  Neutral:  '(._.',
};

const MOOD_RECOMMENDATIONS = {
  Surprise: [
    'Catat momen ini dalam jurnal dan refleksikan apa yang membuatmu terkejut.',
    'Bagikan pengalaman mengejutkan ini dengan orang terdekatmu.',
    'Gunakan rasa penasaran ini untuk mengeksplorasi hal baru yang belum pernah kamu coba.',
    'Ambil napas dalam dan nikmati kejutan sebagai bagian dari perjalanan hidupmu.',
  ],
  Fear: [
    'Coba teknik pernapasan dalam: tarik napas 4 detik, tahan 4 detik, hembuskan 4 detik.',
    'Tuliskan apa yang kamu takutkan dan langkah kecil untuk menghadapinya.',
    'Hubungi seseorang yang kamu percaya dan ceritakan perasaanmu.',
    'Dengarkan musik yang menenangkan dan berikan dirimu waktu untuk beristirahat.',
  ],
  Disgust: [
    'Jauhkan dirimu sejenak dari situasi yang membuatmu tidak nyaman.',
    'Lakukan aktivitas yang kamu sukai untuk mengalihkan pikiran.',
    'Coba berjalan-jalan sebentar untuk menyegarkan pikiran.',
    'Tulis perasaanmu di jurnal untuk memproses emosi yang kamu rasakan.',
  ],
  Happy: [
    'Bagikan kebahagiaanmu dengan orang-orang di sekitarmu!',
    'Manfaatkan energi positif ini untuk menyelesaikan tugas yang tertunda.',
    'Abadikan momen bahagia ini dengan foto atau tulisan di jurnal.',
    'Lakukan kebaikan kecil untuk orang lain dan sebarkan kebahagiaanmu.',
  ],
  Sad: [
    'Izinkan dirimu untuk merasakan kesedihan ini, tidak apa-apa untuk merasa sedih.',
    'Tonton film atau dengarkan lagu favoritmu untuk menghibur diri.',
    'Hubungi teman atau keluarga yang kamu percaya untuk berbicara.',
    'Berjalan-jalanlah di luar ruangan dan hirup udara segar untuk menenangkan pikiran.',
  ],
  Angry: [
    'Tarik napas dalam-dalam dan hitung sampai sepuluh sebelum bereaksi.',
    'Lakukan olahraga ringan seperti jalan cepat atau peregangan untuk melepaskan energi.',
    'Tulis perasaanmu di kertas sebagai cara melepaskan emosi yang terpendam.',
    'Dengarkan musik favorit dan berikan dirimu waktu untuk tenang.',
  ],
  Neutral: [
    'Gunakan momen tenang ini untuk merencanakan tujuan ke depan.',
    'Coba aktivitas baru yang menarik perhatianmu untuk menambah semangat hari ini.',
    'Luangkan waktu untuk membaca buku atau menonton konten yang menginspirasi.',
    'Lakukan meditasi singkat untuk memperkuat ketenangan yang sedang kamu rasakan.',
  ],
};

const POSITIVE_MESSAGES = {
  Surprise: 'Kejutan bisa menjadi awal dari sesuatu yang luar biasa. Tetap terbuka terhadap hal-hal baru yang datang dalam hidupmu.',
  Fear: 'Rasa takut adalah tanda bahwa kamu peduli. Ingat, keberanian bukan berarti tidak takut, tetapi tetap melangkah meski rasa takut itu ada.',
  Disgust: 'Perasaan tidak nyaman ini menunjukkan bahwa kamu memiliki nilai dan batasan yang jelas. Itu adalah hal yang baik.',
  Happy: 'Kebahagiaan yang kamu rasakan saat ini adalah nyata dan berharga. Terus jaga energi positif ini!',
  Sad: 'Setiap kesedihan pasti akan berlalu. Kamu lebih kuat dari yang kamu kira, dan hari yang lebih baik pasti akan datang.',
  Angry: 'Kemarahanmu menunjukkan bahwa kamu peduli. Salurkan energi ini ke arah yang positif dan konstruktif.',
  Neutral: 'Ketenangan adalah kekuatan. Gunakan momen ini untuk refleksi dan persiapan menuju hal-hal yang lebih baik.',
};

function applyMoodTheme(mood) {
  const colors = MOOD_COLORS[mood];
  if (!colors) return;
  const root = document.documentElement;
  root.style.setProperty('--mood-primary', colors.primary);
  root.style.setProperty('--mood-light', colors.light);
  root.style.setProperty('--mood-dark', colors.dark);

  function getLuminance(hex) {
    const r = parseInt(hex.slice(1,3),16)/255;
    const g = parseInt(hex.slice(3,5),16)/255;
    const b = parseInt(hex.slice(5,7),16)/255;
    const toLinear = c => c <= 0.03928 ? c/12.92 : Math.pow((c+0.055)/1.055, 2.4);
    return 0.2126*toLinear(r) + 0.7152*toLinear(g) + 0.0722*toLinear(b);
  }

  const lum = getLuminance(colors.primary);
  const isDark = lum <= 0.45;

  const adaptedText = isDark ? '#ffffff' : '#2B1F1D';
  const adaptedMuted = isDark ? 'rgba(255,255,255,0.65)' : 'rgba(43,31,29,0.65)';

  root.style.setProperty('--mood-text', adaptedText);
  root.style.setProperty('--mood-muted', adaptedMuted);
  root.style.setProperty('--mood-btn-bg', isDark ? '#ffffff' : '#2B1F1D');
  root.style.setProperty('--mood-btn-text', isDark ? colors.primary : '#ffffff');
  root.style.setProperty('--mood-border', isDark ? 'rgba(255,255,255,0.25)' : 'rgba(43,31,29,0.2)');
  root.style.setProperty('--mood-card-bg', isDark ? 'rgba(255,255,255,0.08)' : 'rgba(43,31,29,0.06)');

  const overlay = document.getElementById('mood-overlay');
  if (overlay) {
    overlay.style.background = colors.primary;
    overlay.classList.remove('flash');
    void overlay.offsetWidth;
    overlay.classList.add('flash');
    setTimeout(() => overlay.classList.remove('flash'), 2200);
  }

  document.body.classList.add('mood-active');
}

function resetMoodTheme() {
  document.body.classList.remove('mood-active');
}

function initUploadPage() {
  const uploadZone = document.getElementById('upload-zone');
  const fileInput = document.getElementById('file-input');
  const previewWrap = document.getElementById('preview-wrap');
  const previewImg = document.getElementById('preview-img');
  const previewFilename = document.getElementById('preview-filename');
  const analyzeBtn = document.getElementById('analyze-btn');
  const changeBtn = document.getElementById('change-btn');
  const loadingOverlay = document.getElementById('loading-overlay');
  const resultSection = document.getElementById('result-section');
  const feedbackBtn = document.getElementById('feedback-btn');
  const feedbackInput = document.getElementById('feedback-input');
  const recSection = document.getElementById('rec-section');
  const resetBtn = document.getElementById('reset-btn');

  if (!uploadZone) return;

  let selectedFile = null;
  let currentMood = null;

  uploadZone.addEventListener('click', () => fileInput.click());

  uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.classList.add('dragover');
  });

  uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('dragover'));

  uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) handleFileSelect(file);
  });

  fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) handleFileSelect(file);
  });

  function handleFileSelect(file) {
    selectedFile = file;
    const reader = new FileReader();
    reader.onload = (e) => {
      previewImg.src = e.target.result;
      previewFilename.textContent = file.name;
      uploadZone.style.display = 'none';
      previewWrap.style.display = 'block';
      resultSection.classList.remove('visible');
      recSection.classList.remove('visible');
      resetMoodTheme();
    };
    reader.readAsDataURL(file);
  }

  if (changeBtn) {
    changeBtn.addEventListener('click', () => {
      selectedFile = null;
      fileInput.value = '';
      previewWrap.style.display = 'none';
      uploadZone.style.display = 'block';
      resultSection.classList.remove('visible');
      recSection.classList.remove('visible');
      resetMoodTheme();
      currentMood = null;
    });
  }

  if (analyzeBtn) {
    analyzeBtn.addEventListener('click', async () => {
      if (!selectedFile) return;

      loadingOverlay.classList.add('active');

      const formData = new FormData();
      formData.append('file', selectedFile);

      try {
        const response = await fetch('/predict', { method: 'POST', body: formData });
        const data = await response.json();

        if (data.error) {
          alert('Terjadi kesalahan: ' + data.error);
          loadingOverlay.classList.remove('active');
          return;
        }

        currentMood = data.mood;

        // Apply mood theme
        applyMoodTheme(data.mood);

        // Fill result
        document.getElementById('result-mood-name').textContent = data.mood;
        document.getElementById('result-confidence').textContent = 'Keyakinan: ' + data.confidence + '%';

        // Show result section
        resultSection.classList.add('visible');
        recSection.classList.remove('visible');
        feedbackInput.value = '';
        feedbackBtn.disabled = false;
        feedbackBtn.textContent = 'Kirim';

        loadingOverlay.classList.remove('active');

        // Smooth scroll to result
        setTimeout(() => {
          resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);

      } catch (err) {
        alert('Gagal menghubungi server. Pastikan aplikasi sudah berjalan dengan benar.');
        loadingOverlay.classList.remove('active');
      }
    });
  }

  if (feedbackBtn) {
    feedbackBtn.addEventListener('click', () => {
      const userInput = feedbackInput.value.trim();
      if (!userInput || !currentMood) {
        feedbackInput.focus();
        return;
      }

      feedbackBtn.disabled = true;
      feedbackBtn.textContent = 'Terkirim';

      // Show recommendations
      const recList = document.getElementById('rec-list');
      recList.innerHTML = '';
      const recs = MOOD_RECOMMENDATIONS[currentMood] || [];
      recs.forEach((rec, i) => {
        const item = document.createElement('div');
        item.className = 'rec-item';
        item.innerHTML = `<span class="rec-num">0${i + 1}</span><span>${rec}</span>`;
        recList.appendChild(item);
      });

      document.getElementById('rec-positive').textContent = POSITIVE_MESSAGES[currentMood] || '';

      recSection.classList.add('visible');
      setTimeout(() => {
        recSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 100);
    });
  }

  // ===== MODE TOGGLE =====
  const modeUploadBtn = document.getElementById('mode-upload-btn');
  const modeCameraBtn = document.getElementById('mode-camera-btn');
  const cameraZone = document.getElementById('camera-zone');
  let cameraStream = null;
  let liveDetectInterval = null;
  let facingMode = 'user';

  function stopCamera() {
    if (liveDetectInterval) { clearInterval(liveDetectInterval); liveDetectInterval = null; }
    if (cameraStream) { cameraStream.getTracks().forEach(t => t.stop()); cameraStream = null; }
  }

  async function startCamera() {
    stopCamera();
    try {
      cameraStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode }, audio: false });
      const video = document.getElementById('camera-video');
      video.srcObject = cameraStream;
      // Live detection every 2.5 seconds
      liveDetectInterval = setInterval(() => liveDetect(), 2500);
    } catch (err) {
      alert('Tidak bisa mengakses kamera. Pastikan izin kamera sudah diberikan.');
      setMode('upload');
    }
  }

  async function liveDetect() {
    const video = document.getElementById('camera-video');
    const canvas = document.getElementById('camera-canvas');
    if (!video || video.readyState < 2) return;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.save();
    ctx.scale(-1, 1);
    ctx.drawImage(video, -canvas.width, 0);
    ctx.restore();
    canvas.toBlob(async (blob) => {
      if (!blob) return;
      const fd = new FormData();
      fd.append('file', blob, 'live.jpg');
      try {
        const res = await fetch('/predict', { method: 'POST', body: fd });
        const data = await res.json();
        if (data.mood) {
          const badge = document.getElementById('live-emotion-badge');
          const text = document.getElementById('live-emotion-text');
          const EMOJI = { Surprise:'😲', Fear:'😨', Disgust:'🤢', Happy:'😊', Sad:'😢', Angry:'😠', Neutral:'😐' };
          text.textContent = `${EMOJI[data.mood] || ''} ${data.mood} ${Math.round(data.confidence)}%`;
          badge.classList.add('detected');
        }
      } catch(e) {}
    }, 'image/jpeg', 0.8);
  }

  function setMode(mode) {
    if (mode === 'camera') {
      modeUploadBtn.classList.remove('active');
      modeCameraBtn.classList.add('active');
      uploadZone.style.display = 'none';
      previewWrap.style.display = 'none';
      cameraZone.style.display = 'block';
      resultSection.classList.remove('visible');
      recSection.classList.remove('visible');
      resetMoodTheme();
      startCamera();
    } else {
      modeCameraBtn.classList.remove('active');
      modeUploadBtn.classList.add('active');
      cameraZone.style.display = 'none';
      uploadZone.style.display = 'block';
      stopCamera();
    }
  }

  if (modeUploadBtn) modeUploadBtn.addEventListener('click', () => setMode('upload'));
  if (modeCameraBtn) modeCameraBtn.addEventListener('click', () => setMode('camera'));

  // Flip camera
  const flipBtn = document.getElementById('flip-camera-btn');
  if (flipBtn) {
    flipBtn.addEventListener('click', () => {
      facingMode = facingMode === 'user' ? 'environment' : 'user';
      startCamera();
    });
  }

  // Capture button
  const captureBtn = document.getElementById('capture-btn');
  if (captureBtn) {
    captureBtn.addEventListener('click', async () => {
      const video = document.getElementById('camera-video');
      const canvas = document.getElementById('camera-canvas');
      if (!video || video.readyState < 2) return;
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext('2d');
      ctx.save(); ctx.scale(-1, 1); ctx.drawImage(video, -canvas.width, 0); ctx.restore();
      canvas.toBlob(async (blob) => {
        if (!blob) return;
        stopCamera();
        setMode('upload');
        // Simulate file select with captured blob
        const file = new File([blob], 'capture.jpg', { type: 'image/jpeg' });
        handleFileSelect(file);
      }, 'image/jpeg', 0.92);
    });
  }

  // Stop camera when leaving page
  window.addEventListener('beforeunload', stopCamera);

  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      selectedFile = null;
      fileInput.value = '';
      previewWrap.style.display = 'none';
      uploadZone.style.display = 'block';
      resultSection.classList.remove('visible');
      recSection.classList.remove('visible');
      resetMoodTheme();
      currentMood = null;
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const page = document.body.getAttribute('data-page');
  if (page === 'upload') initUploadPage();
});