// ✅ THREE.js Scene Setup
let scene, camera, renderer;
let textureLoader = new THREE.TextureLoader();
let imagesPath = 'data/'; // Path where images are stored
let imagePlanes = [];
let labels = [];
let movingX = false;
let movingY = false;
let maxImages = 50;
let movementSpeed = 2.0;
let movementAngles = [];
let totalImages = []; // Store all images here

// ✅ Initialize Scene
function init() {
    scene = new THREE.Scene();
    camera = new THREE.OrthographicCamera(
        window.innerWidth / -2, window.innerWidth / 2,
        window.innerHeight / 2, window.innerHeight / -2,
        -500, 1000
    );
    camera.position.z = 1;

    renderer = new THREE.WebGLRenderer({ preserveDrawingBuffer: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setClearColor(0x111111, 1);
    renderer.autoClearColor = false;
    document.body.appendChild(renderer.domElement);

    fetchImages(); // Fetch all image filenames first
    animate();
}

// ✅ Fetch Image List from JSON
async function fetchImages() {
    try {
        const response = await fetch('images.json');
        totalImages = await response.json();

        if (!Array.isArray(totalImages) || totalImages.length === 0) {
            console.error('No images found.');
            return;
        }

        loadImages(); // Load the first batch of images
    } catch (error) {
        console.error('Error loading image list:', error);
    }
} // ✅ FIX: Closing bracket added here!

// ✅ Fade Out Images
function fadeOutImages(callback) {
    let opacity = 1;
    let interval = setInterval(() => {
        opacity -= 0.1;
        imagePlanes.forEach(plane => {
            if (plane.material) plane.material.opacity = opacity;
        });
        if (opacity <= 0) {
            clearInterval(interval);
            callback();
        }
    }, 50);
}

// ✅ Fade In Images
function fadeInImages() {
    let opacity = 0;
    let interval = setInterval(() => {
        opacity += 0.1;
        imagePlanes.forEach(plane => {
            if (plane.material) plane.material.opacity = opacity;
        });
        if (opacity >= 1) {
            clearInterval(interval);
        }
    }, 50);
}

// ✅ Load Images with Optional Filtering
function loadImages(category = '') {
    fadeOutImages(() => {
        clearScene();

        // ✅ Filter images based on category
        let filteredImages = category
            ? totalImages.filter(filename => filename.includes(category))
            : totalImages;

        if (filteredImages.length === 0) {
            console.warn('No images found for category:', category);
            return;
        }

        let shuffledImages = filteredImages.sort(() => 0.5 - Math.random()).slice(0, maxImages);
        displayImages(shuffledImages);
        fadeInImages();
    });
}

// ✅ Display Images with Labels
function displayImages(imageList) {
    clearScene();
    imageList.forEach((filename) => {
        let imagePath = imagesPath + filename;
        let texture = textureLoader.load(imagePath);

        let scaleFactor = Math.random() * 1.5 + 0.1; // 🔥 Random scale 0.1 - 1.6
        let geometry = new THREE.PlaneGeometry(200 * scaleFactor, 200 * scaleFactor);
        let material = new THREE.MeshBasicMaterial({
            map: texture,
            transparent: true,
            side: THREE.DoubleSide
        });

        let plane = new THREE.Mesh(geometry, material);
        let x = (Math.random() * window.innerWidth) - window.innerWidth / 2;
        let y = (Math.random() * window.innerHeight) - window.innerHeight / 2;
        plane.position.set(x, y, 0);

        let angle = Math.random() * Math.PI * 2; // 🔥 Randomize movement angles
        movementAngles.push({
            angle,
            directionX: Math.random() > 0.5 ? 1 : -1, // 🔥 Random direction
            directionY: Math.random() > 0.5 ? 1 : -1  // 🔥 Random direction
        });

        scene.add(plane);
        imagePlanes.push(plane);

        createLabel(filename, plane);
    });

    updateLabels();
}

// ✅ Create Labels for Each Image
function createLabel(text, plane) {
    let label = document.createElement('div');
    label.classList.add('image-label');
    label.innerText = text;
    document.body.appendChild(label);
    labels.push({ element: label, plane });
}

// ✅ Update Labels to Move with Images
function updateLabels() {
    labels.forEach(({ element, plane }) => {
        let screenPosition = plane.position.clone().project(camera);
        let x = (screenPosition.x * 0.5 + 0.5) * window.innerWidth;
        let y = (1 - (screenPosition.y * 0.5 + 0.5)) * window.innerHeight;

        element.style.left = `${x}px`;
        element.style.top = `${y}px`;
        element.style.transform = "translate(-50%, 20px)"; // 🔥 Adjusted to appear below image
    });
}

// ✅ Clear Scene Before Reloading
function clearScene() {
    imagePlanes.forEach(plane => scene.remove(plane));
    labels.forEach(labelObj => document.body.removeChild(labelObj.element));
    imagePlanes = [];
    labels = [];
    movementAngles = [];
}

// ✅ Animation Function
function animate() {
    requestAnimationFrame(animate);

    if (movingX || movingY) {
        imagePlanes.forEach((plane, index) => {
            let { angle, directionX, directionY } = movementAngles[index];

            if (movingX) {
                plane.position.x += Math.cos(angle) * movementSpeed * directionX;
            }
            if (movingY) {
                plane.position.y += Math.sin(angle) * movementSpeed * directionY;
            }

            // Wrap around edges
            if (plane.position.x > window.innerWidth / 2) plane.position.x = -window.innerWidth / 2;
            if (plane.position.x < -window.innerWidth / 2) plane.position.x = window.innerWidth / 2;
            if (plane.position.y > window.innerHeight / 2) plane.position.y = -window.innerHeight / 2;
            if (plane.position.y < -window.innerHeight / 2) plane.position.y = window.innerHeight / 2;
        });

        updateLabels();
    }

    renderer.render(scene, camera);
}

// ✅ Keyboard Controls for Filtering
window.addEventListener('keydown', (event) => {
    switch (event.key) {
        case '1': loadImages('Y1S1'); break;
        case '2': loadImages('Y2S1'); break;
        case '3': loadImages('Y3S1'); break;
        case '4': loadImages('Y4S1'); break;
        case 'r': loadImages(); break; // 🔥 Randomize images
        case 'b': location.reload(); break; // 🔥 Restart
        case 'x': movingX = !movingX; movingY = false; break; // 🔥 Toggle movement modes
    }
});

init();
