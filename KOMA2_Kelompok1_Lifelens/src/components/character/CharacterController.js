import { gsap } from "gsap";

const STATES = ["neutral", "happy", "sad", "tired", "worried", "calm", "alert"];

export class CharacterController {
  constructor(rootSelector = "#rina-character") {
    this.rootSelector = rootSelector;
    this.currentState = "neutral";
    this.idleTimeline = null;
  }

  init() {
    this.setState(this.currentState);

    this.idleTimeline = gsap.timeline({ repeat: -1, yoyo: true });
    this.idleTimeline.to(`${this.rootSelector} #body`, {
      y: -3,
      duration: 1.8,
      ease: "sine.inOut",
    });

    gsap.to(`${this.rootSelector} #eyes`, {
      scaleY: 0.08,
      transformOrigin: "center",
      duration: 0.08,
      repeat: -1,
      repeatDelay: 3.8,
      yoyo: true,
    });
  }

  setState(newState) {
    if (!STATES.includes(newState)) {
      throw new Error(`Unknown RINA state: ${newState}`);
    }

    gsap.to(`${this.rootSelector} [id^="expression-"]`, {
      opacity: 0,
      duration: 0.2,
      overwrite: true,
    });

    gsap.to(`${this.rootSelector} #expression-${newState}`, {
      opacity: 1,
      duration: 0.25,
      overwrite: true,
    });

    this.currentState = newState;
  }

  setMouthOpen(amount) {
    const clamped = Math.max(0, Math.min(1, amount));
    gsap.to(`${this.rootSelector} #mouth`, {
      scaleY: 0.35 + clamped,
      transformOrigin: "center",
      duration: 0.08,
      overwrite: true,
    });
  }

  destroy() {
    if (this.idleTimeline) {
      this.idleTimeline.kill();
      this.idleTimeline = null;
    }
  }
}

export default CharacterController;
