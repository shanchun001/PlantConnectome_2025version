document.addEventListener("DOMContentLoaded", function() {
    // Add click event listeners to all images
    var images = document.getElementsByTagName('img');
    for (var i = 0; i < images.length; i++) {
        images[i].addEventListener('click', openLightbox);
    }

    function openLightbox(event) {
        event.preventDefault();

        var img = event.target;
        var overlay = document.createElement('div');
        var lightbox = document.createElement('div');
        var imgClone = img.cloneNode(true);
        imgClone.classList.add('lightbox-image');
        imgClone.style.maxWidth = '90vw';
        imgClone.style.maxHeight = '90vh';
        imgClone.style.left = 0;
        const scaleFactor = Math.min(1.5, 0.9 * window.innerWidth / (img.width * 1.5), 0.9 * window.innerHeight / (img.height * 1.5));
        imgClone.style.transform = `scale(${Math.max(1, scaleFactor)})`;

        // Set up the overlay
        overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
        overlay.style.position = 'fixed';
        overlay.style.top = '0';
        overlay.style.bottom = '0';
        overlay.style.left = '0';
        overlay.style.right = '0';
        overlay.style.zIndex = '999';
        overlay.id = 'overlay';

        // Set up the lightbox
        lightbox.style.position = 'fixed';
        lightbox.style.top = '50%';
        lightbox.style.left = '50%';
        lightbox.style.transform = 'translate(-50%, -50%)';
        lightbox.style.zIndex = '1000';
        lightbox.id = 'lightbox';
        lightbox.appendChild(imgClone);

        // Add event listener to close lightbox when clicking outside of it
        overlay.addEventListener('click', closeLightbox);
        imgClone.addEventListener('click', function(e) {
            e.stopPropagation();
        });

        // Append the overlay and lightbox to the body
        document.body.appendChild(overlay);
        document.body.appendChild(lightbox);
    }

    function closeLightbox(event) {
        var overlay = document.getElementById('overlay');
        var lightbox = document.getElementById('lightbox');

        // Remove the overlay and lightbox
        document.body.removeChild(overlay);
        document.body.removeChild(lightbox);

        // Enable scrolling on the body again
        document.body.style.overflow = 'auto';
    }
});