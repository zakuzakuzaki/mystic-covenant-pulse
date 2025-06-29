// 3Dビューアークラス
class ThreeJSViewer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.model = null;
        this.init();
    }

    init() {
        // シーンの作成
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x222222);

        // カメラの作成
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;
        this.camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
        this.camera.position.set(0, 0, 50);

        // レンダラーの作成
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(width, height);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.container.appendChild(this.renderer.domElement);

        // オービットコントロールの追加
        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.enableZoom = true;
        this.controls.enablePan = true;

        // ライティングの設定
        this.setupLighting();

        // アニメーションループの開始
        this.animate();

        // リサイズイベントの設定
        window.addEventListener('resize', () => this.onWindowResize());
    }

    setupLighting() {
        // 環境光
        const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
        this.scene.add(ambientLight);

        // 方向光1
        const directionalLight1 = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight1.position.set(50, 50, 50);
        directionalLight1.castShadow = true;
        directionalLight1.shadow.mapSize.width = 2048;
        directionalLight1.shadow.mapSize.height = 2048;
        this.scene.add(directionalLight1);

        // 方向光2
        const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.4);
        directionalLight2.position.set(-50, -50, 50);
        this.scene.add(directionalLight2);
    }

    loadSTL(modelPath) {
        return new Promise((resolve, reject) => {
            const loader = new THREE.STLLoader();
            
            loader.load(
                modelPath,
                (geometry) => {
                    this.clearModel();
                    
                    // マテリアルの作成
                    const material = new THREE.MeshLambertMaterial({
                        color: 0xffaa88,
                        side: THREE.DoubleSide
                    });

                    // メッシュの作成
                    this.model = new THREE.Mesh(geometry, material);
                    this.model.castShadow = true;
                    this.model.receiveShadow = true;

                    // モデルの中央配置とスケーリング
                    this.centerAndScaleModel(geometry);

                    this.scene.add(this.model);
                    resolve(true);
                },
                (progress) => {
                    console.log('Loading progress:', (progress.loaded / progress.total * 100) + '%');
                },
                (error) => {
                    console.error('STL loading error:', error);
                    reject(error);
                }
            );
        });
    }

    centerAndScaleModel(geometry) {
        // バウンディングボックスの計算
        geometry.computeBoundingBox();
        const box = geometry.boundingBox;
        const center = new THREE.Vector3();
        box.getCenter(center);
        
        // モデルの中央配置
        geometry.translate(-center.x, -center.y, -center.z);

        // スケーリング
        const size = new THREE.Vector3();
        box.getSize(size);
        const maxDim = Math.max(size.x, size.y, size.z);
        const scale = 30 / maxDim;
        this.model.scale.setScalar(scale);
    }

    clearModel() {
        if (this.model) {
            this.scene.remove(this.model);
            this.model = null;
        }
    }

    onWindowResize() {
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;
        
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
    }

    animate() {
        requestAnimationFrame(() => this.animate());
        
        this.controls.update();
        this.renderer.render(this.scene, this.camera);
    }

    // モデルの色を変更
    setModelColor(color) {
        if (this.model && this.model.material) {
            this.model.material.color.setHex(color);
        }
    }

    // アニメーション効果
    addPulseEffect() {
        if (this.model) {
            const originalScale = this.model.scale.x;
            const pulseAnimation = () => {
                const time = Date.now() * 0.002;
                const scale = originalScale + Math.sin(time) * 0.1;
                this.model.scale.setScalar(scale);
                requestAnimationFrame(pulseAnimation);
            };
            pulseAnimation();
        }
    }
}

// グローバル3Dビューアー管理
const viewers = {
    creature1: null,
    creature2: null
};