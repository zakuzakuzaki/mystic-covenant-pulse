import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader.js';

/**
 * 3Dビューアークラス
 */
export class ThreeJSViewer {
    private container: HTMLElement;
    private scene: THREE.Scene | null = null;
    private camera: THREE.PerspectiveCamera | null = null;
    private renderer: THREE.WebGLRenderer | null = null;
    private controls: OrbitControls | null = null;
    private model: THREE.Mesh | null = null;

    constructor(containerId: string) {
        const container = document.getElementById(containerId);
        if (!container) {
            throw new Error(`Container with id '${containerId}' not found`);
        }
        this.container = container;
        this.init();
    }

    private init(): void {
        // シーンの作成
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x222222);

        // カメラの作成
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;
        this.camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
        this.camera.position.set(0, -30, 0); // Y軸方向から見る（下から上へ）
        this.camera.lookAt(0, 0, 0); // 原点を見る

        // レンダラーの作成
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(width, height);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.container.appendChild(this.renderer.domElement);

        // オービットコントロールの追加
        this.controls = new OrbitControls(this.camera, this.renderer.domElement);
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

    private setupLighting(): void {
        if (!this.scene) return;

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

    public async loadSTL(modelPath: string): Promise<void> {
        return new Promise((resolve, reject) => {
            const loader = new STLLoader();
            
            loader.load(
                modelPath,
                (geometry: THREE.BufferGeometry) => {
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

                    if (this.scene) {
                        this.scene.add(this.model);
                    }
                    resolve();
                },
                (progress: ProgressEvent) => {
                    console.log('Loading progress:', (progress.loaded / progress.total * 100) + '%');
                },
                (error: unknown) => {
                    console.error('STL loading error:', error);
                    reject(error);
                }
            );
        });
    }

    private centerAndScaleModel(geometry: THREE.BufferGeometry): void {
        if (!this.model) return;

        // バウンディングボックスの計算
        geometry.computeBoundingBox();
        const box = geometry.boundingBox;
        if (!box) return;

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

    public clearModel(): void {
        if (this.model && this.scene) {
            this.scene.remove(this.model);
            this.model = null;
        }
    }

    private onWindowResize(): void {
        if (!this.camera || !this.renderer) return;

        const width = this.container.clientWidth;
        const height = this.container.clientHeight;
        
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
    }

    private animate(): void {
        requestAnimationFrame(() => this.animate());
        
        if (this.controls) {
            this.controls.update();
        }
        if (this.renderer && this.scene && this.camera) {
            this.renderer.render(this.scene, this.camera);
        }
    }

    /**
     * モデルの色を変更
     */
    public setModelColor(color: number): void {
        if (this.model && this.model.material) {
            (this.model.material as THREE.MeshLambertMaterial).color.setHex(color);
        }
    }

    /**
     * アニメーション効果
     */
    public addPulseEffect(): void {
        if (this.model) {
            const originalScale = this.model.scale.x;
            const pulseAnimation = (): void => {
                if (!this.model) return;
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
export const viewers = {
    creature1: undefined as ThreeJSViewer | undefined,
    creature2: undefined as ThreeJSViewer | undefined
};