document.addEventListener("DOMContentLoaded", function() {
    const collage = document.getElementById('animatedCollage');
    collage.addEventListener('mouseenter', function() {
        Array.from(collage.children).forEach(img => {
            img.style.animationPlayState = 'paused';
        });
    });
    collage.addEventListener('mouseleave', function() {
        Array.from(collage.children).forEach(img => {
            img.style.animationPlayState = 'running';
        });
    });
});

document.getElementById('toggle-sidebar').addEventListener('click', function() {
    const sidebar = document.getElementById('sidebar');
    const content = document.querySelector('.content');
    sidebar.classList.toggle('open'); // Toggle sidebar open class
    content.classList.toggle('shift'); // Shift content
});
