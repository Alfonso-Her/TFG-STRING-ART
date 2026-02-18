document.addEventListener("DOMContentLoaded", () => {
    const observer = new MutationObserver(() => {
        const imgs = document.querySelectorAll(".Imagen img, .imagen-especial img");

        imgs.forEach(img => {
            if (img.dataset.zoomable) return;
            img.dataset.zoomable = true;
            img.classList.add("zoomable-img");

            let scale = 1;
            let zoomActivo = false;
            let resetTimer = null;

            // Click derecho activa/desactiva el modo zoom
            img.addEventListener("contextmenu", e => {
                e.preventDefault();
                zoomActivo = !zoomActivo;
                img.style.cursor = zoomActivo ? "zoom-in" : "default";

                if (!zoomActivo) {
                    scale = 1;
                    img.style.transformOrigin = "center center";
                    img.style.transform = "scale(1)";
                }
            });

            // Rueda del ratón solo si el zoom está activo
            img.addEventListener("wheel", e => {
                if (!zoomActivo) return;
                e.preventDefault();

                const delta = e.deltaY > 0 ? -0.1 : 0.1;
                scale = Math.min(Math.max(1, scale + delta), 5);

                const rect = img.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                const xPercent = (x / rect.width) * 100;
                const yPercent = (y / rect.height) * 100;

                img.style.transformOrigin = `${xPercent}% ${yPercent}%`;
                img.style.transform = `scale(${scale})`;

                if (resetTimer) clearTimeout(resetTimer);
                resetTimer = setTimeout(() => {
                    scale = 1;
                    img.style.transformOrigin = "center center";
                    img.style.transform = "scale(1)";
                    zoomActivo = false;
                    img.style.cursor = "default";
                }, 30000);
            });

            // Control del temporizador
            img.addEventListener("mouseleave", () => {
                if (resetTimer) clearTimeout(resetTimer);
                resetTimer = setTimeout(() => {
                    scale = 1;
                    img.style.transformOrigin = "center center";
                    img.style.transform = "scale(1)";
                    zoomActivo = false;
                    img.style.cursor = "default";
                }, 30000);
            });

            img.addEventListener("mouseenter", () => {
                if (resetTimer) clearTimeout(resetTimer);
            });
        });
    });

    observer.observe(document.body, { childList: true, subtree: true });
});