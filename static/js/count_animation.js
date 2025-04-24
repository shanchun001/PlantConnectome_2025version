const animation_duration = 3000;                                     // The animation will be 3 seconds long.
const frames_per_sec = 1000 / 60;                                    // 60 actions per second.
const num_frames = Math.round(animation_duration / frames_per_sec);  // How many frames should the animation have?
const ease_out = t => t * (2 - t);                                 // Easing out function for animation.

const animate = (element) => {
    let frame = 0;
    const count_to = parseInt(element.innerHTML, 10)
    const counter = setInterval(() => {
        frame++;
        const progress = ease_out(frame / num_frames);
        const current_count = Math.round(count_to * progress);

        if (parseInt(element.innerText, 10) !== current_count) {
            element.innerText = current_count;
        }

        if (frame === num_frames) {
            clearInterval(counter);
        }

    }, frames_per_sec);
};

window.addEventListener('load', () => {
    let to_animate = document.querySelectorAll('.count');
    to_animate.forEach(animate);
})