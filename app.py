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

const categories = ['Y1S1', 'Y2S1', 'Y3S1', 'Y4S1'];

// ✅ Loading Overlay
window.addEventListener('load', () => {
    document.getElementById('loadingOverlay').style.display = 'none';
});

// Debug logging with timestamp
function debugLog(message, data) {
    const timestamp = new Date().toISOString().substr(11, 8);
    console.log(`[${timestamp}] ${message}`);
    if (data !== undefined) {
        console.log(data);
    }
}

// Check if images.json was loaded correctly
function validateImageData() {
    debugLog(`Total images in memory: ${totalImages.length}`);
    if (totalImages.length === 0) {
        debugLog('WARNING: No images loaded');
        return false;
    }
    
    // Check for current category
    const currentCategory = categories[currentCategoryIndex];
    const matchingImages = totalImages.filter(name => name.includes(currentCategory));
    debugLog(`Images matching category '${currentCategory}': ${matchingImages.length}`);
    
    return true;
}

// ✅ Fetch Images
async function fetchImages() {
    try {
        debugLog('Fetching images.json...');
        const res = await fetch('/images.json');
        
        if (!res.ok) {
            throw new Error(`Failed to fetch images.json: ${res.status} ${res.statusText}`);
        }
        
        totalImages = await res.json();
        debugLog(`Loaded ${totalImages.length} images from images.json`);
        
        // Validate the response
        if (!Array.isArray(totalImages)) {
            throw new Error('images.json did not return an array');
        }
        
        loadImages(categories[currentCategoryIndex]);
    } catch (err) {
        console.error('Failed to fetch images.json:', err);
        alert('Failed to load images. Check console for details.');
    }
}

// ✅ Load and Display Images
function loadImages(category = '') {
    debugLog(`Loading images for category: ${category}`);
    clearScene();

    const filtered = category
        ? totalImages.filter(name => name.includes(category))
        : totalImages;
    
    debugLog(`Filtered ${filtered.length} images matching category "${category}"`);

    if (filtered.length === 0) {
        debugLog(`WARNING: No images found for category "${category}"`);
        return;
    }

    const selected = filtered.sort(() => 0.5 - Math.random()).slice(0, maxImages);
    debugLog(`Selected ${selected.length} random images to display`);

    selected.forEach((filename) => {
        const tex = textureLoader.load(
            `data/${filename}`,
            // Success callback
            () => debugLog(`Loaded texture: ${filename}`),
            // Progress callback
            undefined,
            // Error callback
            (err) => console.error(`Failed to load texture: ${filename}`, err)
        );
        
        let randomwidth = Math.random() * (250 - 50) + 50;
        const geo = new THREE.PlaneGeometry(randomwidth, randomwidth);
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
        element.style.color = 'cyan';
        element.style.fontSize = '12px';
    });
}

// ✅ Clear Scene
function clearScene() {
    debugLog(`Clearing scene: removing ${imagePlanes.length} planes and ${labels.length} labels`);
    
    imagePlanes.forEach(p => scene.remove(p));
    imagePlanes = [];
    movementAngles = [];

    labels.forEach(({ element }) => element.remove());
    labels = [];
}

// ✅ Animate with Trails
function animate() {
    requestAnimationFrame(animate);

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
}

// ✅ Init Scene
function init() {
    debugLog('Initializing scene');
    
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
    
    // Handle window resize
    window.addEventListener('resize', () => {
        camera.left = window.innerWidth / -2;
        camera.right = window.innerWidth / 2;
        camera.top = window.innerHeight / 2;
        camera.bottom = window.innerHeight / -2;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
}

// ✅ Keyboard Events
let qrDownCount = 0;
let qrDownTimer = null;

window.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowDown') {
        if (!movingX && !movingY) {
            movingX = true;
            debugLog('Movement: X enabled');
        } else if (movingX) {
            movingX = false;
            movingY = true;
            debugLog('Movement: Y enabled');
        } else {
            movingX = false;
            movingY = false;
            debugLog('Movement: disabled');
        }
    } else if (e.key === 'ArrowLeft') {
        handleQRPress();
    } else if (e.key === 'ArrowRight') {
        currentCategoryIndex = (currentCategoryIndex + 1) % categories.length;
        debugLog(`Switching to category: ${categories[currentCategoryIndex]}`);
        loadImages(categories[currentCategoryIndex]);
    } else if (e.key === 'r') {
        sortAndReloadImages('r');
    } else if (e.key === 'g') {
        sortAndReloadImages('g');
    } else if (e.key === 'b') {
        sortAndReloadImages('b');
    } else if (e.key === 'l') {
        sortAndReloadImages('luminance');
    }
});

// ✅ UI Buttons
['r', 'g', 'b', 'l'].forEach(k => {
    const btn = document.getElementById(`sort-${k}`);
    if (btn) btn.onclick = () => sortAndReloadImages(k === 'l' ? 'luminance' : k);
});

// ✅ QR Button
if (document.getElementById('leftBtn')) {
    document.getElementById('leftBtn').onclick = () => handleQRPress();
}

// ✅ QR Functions
function handleQRPress() {
    qrDownCount++;
    debugLog(`QR button press count: ${qrDownCount}`);
    
    if (qrDownTimer) clearTimeout(qrDownTimer);

    qrDownTimer = setTimeout(() => qrDownCount = 0, 3000);

    if (qrDownCount >= 2) {
        captureCanvasToQR();
        qrDownCount = 0;
    }
}

function captureCanvasToQR(retryCount = 0) {
    debugLog('Capturing canvas for QR code');
    
    const canvas = document.querySelector('canvas');
    if (!canvas) {
        if (retryCount < 5) {
            debugLog(`Canvas not found, retrying (${retryCount + 1}/5)...`);
            setTimeout(() => captureCanvasToQR(retryCount + 1), 300);
        } else {
            alert("Canvas not found after multiple attempts!");
        }
        return;
    }

    const dataURL = canvas.toDataURL('image/jpeg', 0.7);
    debugLog('Canvas captured, sending to server');
    
    fetch('/generate-qr', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `image_data=${encodeURIComponent(dataURL)}`
    })
    .then(res => {
        if (!res.ok) {
            throw new Error(`Server responded with status: ${res.status}`);
        }
        return res.json();
    })
    .then(data => {
        if (data.success) {
            debugLog('QR code generated successfully');
            showQR(data.qr_code, data.original_image);
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
    debugLog(`Showing QR code: ${qrURL} (links to ${linkURL})`);
    
    const qrContainer = document.getElementById('qrCodeContainer');
    const qrContent = document.getElementById('qrContent');

    qrContent.innerHTML = `<img src="${qrURL}" />`;
    qrContainer.style.display = 'block';

    setTimeout(() => {
        debugLog('QR code display timeout reached, hiding');
        qrContent.innerHTML = '';
        qrContainer.style.display = 'none';
    }, 7000);
}

function sortAndReloadImages(metric) {
    const category = categories[currentCategoryIndex];
    
    debugLog(`Sorting images by ${metric} in category ${category}`);
    
    fetch(`/sorted-images?metric=${metric}&category=${category}`)
        .then(res => {
            if (!res.ok) {
                throw new Error(`Server responded with status: ${res.status}`);
            }
            return res.json();
        })
        .then(sortedList => {
            debugLog(`Received ${sortedList.length} sorted images`);
            
            // Clear existing images
            clearScene();
            
            if (sortedList.length === 0) {
                console.warn('No images returned from the server');
                return;
            }
            
            // Load the sorted images
            sortedList.slice(0, maxImages).forEach(filename => {
                const tex = textureLoader.load(`data/${filename}`, 
                    // Success callback
                    function() {
                        debugLog(`Successfully loaded texture: ${filename}`);
                    },
                    // Progress callback
                    undefined,
                    // Error callback
                    function(err) {
                        console.error(`Error loading texture ${filename}:`, err);
                    }
                );
                
                let randomwidth = Math.random() * (250 - 50) + 50;
                const geo = new THREE.PlaneGeometry(randomwidth, randomwidth);
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
        })
        .catch(err => {
            console.error('Failed to fetch or display sorted images:', err);
            alert('Error sorting images. Check console for details.');
        });
}

// Initialize the application
init();
