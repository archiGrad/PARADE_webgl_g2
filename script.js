// ✅ Core Setup
let scene, camera, renderer;
let textureLoader = new THREE.TextureLoader();
let imagePlanes = [];
let movementAngles = [];
let totalImages = [];
let labels = [];
let currentCategoryIndex = 0;
let maxImages = 50;
let movementSpeed = 1.2;
let movingX = false;
let movingY = false;

const categories = ['Y1', 'Y2', 'Y3', 'Y4'];

// ✅ Loading Overlay
window.addEventListener('load', () => {
    document.getElementById('loadingOverlay').style.display = 'none';
});

// ✅ FPS Stats
const stats = new Stats();
stats.showPanel(0);
document.body.appendChild(stats.dom);
stats.dom.style.position = 'absolute';
stats.dom.style.left = '0px';
stats.dom.style.top = '0px';

// ✅ Fetch Images
async function fetchImages() {
    try {
        const res = await fetch('/images.json');
        totalImages = await res.json();
        loadImages(categories[currentCategoryIndex]);
    } catch (err) {
        console.error('Failed to fetch images.json:', err);
    }
}

// ✅ Load and Display Images
function loadImages(category = '') {
    clearScene();

    const filtered = category
        ? totalImages.filter(name => name.includes(category))
        : totalImages;

    const selected = filtered.sort(() => 0.5 - Math.random()).slice(0, maxImages);

    selected.forEach((filename) => {
        const tex = textureLoader.load(`data/${filename}`);
        const geo = new THREE.PlaneGeometry(200, 200);
        const mat = new THREE.MeshBasicMaterial({ map: tex, transparent: true });
        const plane = new THREE.Mesh(geo, mat);

        plane.position.set(
            (Math.random() - 0.5) * window.innerWidth,
            (Math.random() - 0.5) * window.innerHeight,
            0
        );

        movementAngles.push({
            angle: Math.random() * Math.PI * 2,
            dx: Math.random() > 0.5 ? 1 : -1,
            dy: Math.random() > 0.5 ? 1 : -1
        });

        scene.add(plane);
        imagePlanes.push(plane);
        createLabel(filename, plane);
    });

    updateLabels();
}

// ✅ Create Label
function createLabel(filename, plane) {
    const label = document.createElement('div');
    label.className = 'image-label';
    label.innerText = filename;
    document.body.appendChild(label);
    labels.push({ element: label, plane });
}

// ✅ Update Label Positions
function updateLabels() {
    labels.forEach(({ element, plane }) => {
        const screenPos = plane.position.clone().project(camera);
        const x = (screenPos.x * 0.5 + 0.5) * window.innerWidth;
        const y = (1 - (screenPos.y * 0.5 + 0.5)) * window.innerHeight;

        element.style.left = `${x}px`;
        element.style.top = `${y}px`;
        element.style.position = 'absolute';
        element.style.pointerEvents = 'none';
        element.style.transform = 'translate(-50%, -10px)';
        element.style.color = 'limegreen';
        element.style.fontSize = '12px';
    });
}

// ✅ Clear Scene
function clearScene() {
    imagePlanes.forEach(p => scene.remove(p));
    imagePlanes = [];
    movementAngles = [];

    labels.forEach(({ element }) => element.remove());
    labels = [];
}

// ✅ Animate with Trails
function animate() {
    requestAnimationFrame(animate);
    stats.begin();

    imagePlanes.forEach((plane, i) => {
        const { angle, dx, dy } = movementAngles[i];

        if (movingX) {
            plane.position.x += Math.cos(angle) * movementSpeed * dx;
        }
        if (movingY) {
            plane.position.y += Math.sin(angle) * movementSpeed * dy;
        }

        const w = window.innerWidth / 2;
        const h = window.innerHeight / 2;
        if (plane.position.x > w) plane.position.x = -w;
        if (plane.position.x < -w) plane.position.x = w;
        if (plane.position.y > h) plane.position.y = -h;
        if (plane.position.y < -h) plane.position.y = h;
    });

    updateLabels();
    renderer.clearDepth();
    renderer.render(scene, camera);
    stats.end();
}

// ✅ Init Scene
function init() {
    scene = new THREE.Scene();
    camera = new THREE.OrthographicCamera(
        window.innerWidth / -2, window.innerWidth / 2,
        window.innerHeight / 2, window.innerHeight / -2,
        -1000, 1000
    );
    camera.position.z = 1;

    renderer = new THREE.WebGLRenderer({ preserveDrawingBuffer: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setClearColor(0x000000, 1);
    renderer.autoClear = false;
    document.body.appendChild(renderer.domElement);

    fetchImages();
    animate();
}

// ✅ Keyboard Events
let qrPressCount = 0;
let qrTimer = null;

window.addEventListener('keydown', (e) => {
    switch (e.key.toLowerCase()) {
        case 'x':
            if (!movingX && !movingY) {
                movingX = true;
            } else if (movingX) {
                movingX = false;
                movingY = true;
            } else {
                movingX = false;
                movingY = false;
            }
            break;

        case '1':
            loadImages('Y1');
            break;
        case '2':
            loadImages('Y2');
            break;
        case '3':
            loadImages('Y3');
            break;
        case '4':
            loadImages('Y4');
            break;
        case 'r':
            loadImages();
            break;

        case 'q':
            qrPressCount++;
            if (qrTimer) clearTimeout(qrTimer);
            qrTimer = setTimeout(() => qrPressCount = 0, 3000);
            if (qrPressCount >= 2) {
                captureCanvasToQR();
                qrPressCount = 0;
            }
            break;
    }
});

// ✅ UI Buttons
document.getElementById('moveBtn')?.addEventListener('click', () => {
    if (!movingX && !movingY) {
        movingX = true;
    } else if (movingX) {
        movingX = false;
        movingY = true;
    } else {
        movingX = false;
        movingY = false;
    }
});

document.getElementById('randomBtn')?.addEventListener('click', () => loadImages());
document.getElementById('btnY1')?.addEventListener('click', () => loadImages('Y1'));
document.getElementById('btnY2')?.addEventListener('click', () => loadImages('Y2'));
document.getElementById('btnY3')?.addEventListener('click', () => loadImages('Y3'));
document.getElementById('btnY4')?.addEventListener('click', () => loadImages('Y4'));

// ✅ QR Functions
function captureCanvasToQR(retryCount = 0) {
    const canvas = document.querySelector('canvas');
    if (!canvas) {
        if (retryCount < 5) {
            setTimeout(() => captureCanvasToQR(retryCount + 1), 300);
        } else {
            alert("Canvas not found after multiple attempts!");
        }
        return;
    }

    const dataURL = canvas.toDataURL('image/jpeg', 0.7);

    fetch('/generate-qr', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `image_data=${encodeURIComponent(dataURL)}`
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            showQR(data.qr_code, data.original_image);

            setTimeout(() => {
                document.getElementById('qrCodeContainer').style.display = 'none';
                clearScene();
                fetchImages();
                movingX = false;
                movingY = false;
            }, 5000);
        } else {
            console.error('QR generation failed:', data.error);
            alert('QR generation failed: ' + data.error);
        }
    })
    .catch(err => {
        console.error('QR fetch error:', err);
        alert('QR upload error');
    });
}

function showQR(qrURL, linkURL) {
    const qrContainer = document.getElementById('qrCodeContainer');
    const qrContent = document.getElementById('qrContent');
    qrContent.innerHTML = `
        <img src="${qrURL}" style="max-width: 200px; margin-bottom: 10px;" />
        <br><a href="${linkURL}" target="_blank">${linkURL}</a>
    `;
    qrContainer.style.display = 'block';
}

// ✅ Boot
init();
