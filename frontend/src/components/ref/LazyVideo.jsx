import { useEffect, useRef } from "react";

export default function LazyVideo({ src, webm, mobileSrc, poster, className = "", testId, defer = false }) {
  const ref = useRef(null);

  useEffect(() => {
    const video = ref.current;
    if (!video) return;
    let io;
    const arm = () => {
      io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          if (!video.dataset.loaded) {
            video.dataset.loaded = "1";
            const isMobile = typeof window !== "undefined" && window.matchMedia("(max-width: 768px)").matches;
            if (webm && !isMobile) {
              const s = document.createElement("source");
              s.src = webm;
              s.type = "video/webm";
              video.appendChild(s);
            }
            const s2 = document.createElement("source");
            s2.src = isMobile && mobileSrc ? mobileSrc : src;
            s2.type = "video/mp4";
            video.appendChild(s2);
            video.load();
          }
          video.play().catch(() => {});
        });
      },
      { rootMargin: "400px" }
      );
      io.observe(video);
    };
    if (defer && document.readyState !== "complete") {
      window.addEventListener("load", arm, { once: true });
    } else {
      arm();
    }
    return () => io && io.disconnect();
  }, [src, webm, mobileSrc, defer]);

  return (
    <video
      ref={ref}
      className={className}
      autoPlay
      muted
      loop
      playsInline
      preload="none"
      poster={poster}
      onCanPlay={(e) => { const v = e.currentTarget; if (v.paused) v.play().catch(() => {}); }}
      data-testid={testId}
    />
  );
}
