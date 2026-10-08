/* The commissioned artwork is displaced gently; the interface stays HTML. */
(() => {
  "use strict";
  const root = document.querySelector(".ts-landing");
  if (!root) return;
  const art = root.querySelector(".ts-art");
  const image = art.querySelector("img");
  const canvas = art.querySelector("canvas");
  const toggle = root.querySelector(".ts-motion");
  const text = toggle.querySelector(".ts-motion-text");
  const reduced = matchMedia("(prefers-reduced-motion: reduce)");
  const coarse = matchMedia("(pointer: coarse)");
  let paused = false, visible = true, frame = 0, time = 0, last = 0;
  let pointer = [0, 0], target = [0, 0];
  let gl, program, texture, buffer;
  let ready = false, disposed = false;
  const vertex = [
    "attribute vec2 position;", "varying vec2 uv;",
    "void main() { uv = (position + 1.0) * 0.5; gl_Position = vec4(position, 0.0, 1.0); }"
  ].join("\n");
  const fragment = [
    "precision mediump float;",
    "varying vec2 uv;",
    "uniform sampler2D artwork;",
    "uniform vec2 resolution, imageSize, pointer;",
    "uniform float time;",
    "void main() {",
    "  float screenAspect = resolution.x / resolution.y;",
    "  float imageAspect = imageSize.x / imageSize.y;",
    "  vec2 cover = screenAspect > imageAspect",
    "    ? vec2(1.0, imageAspect / screenAspect) : vec2(screenAspect / imageAspect, 1.0);",
    "  vec2 p = (uv - 0.5) * cover + 0.5;",
    // Restrict deformation to the sculpture above the quiet text region.
    "  float region = smoothstep(0.26, 0.68, p.y);",
    "  float wave = sin(p.x * 6.0 + p.y * 3.0 + time * 0.42);",
    "  float counterWave = cos(p.x * 3.6 - p.y * 4.0 - time * 0.28);",
    "  p.x += region * (counterWave * 0.009 + pointer.x * 0.006);",
    "  p.y += region * (wave * 0.019 + pointer.y * 0.008);",
    "  p = clamp(p, vec2(0.001), vec2(0.999));",
    "  vec3 color = texture2D(artwork, p).rgb;",
    "  float lime = smoothstep(0.04, 0.22, color.g - color.b);",
    "  float light = 1.0 + region * lime * (wave * 0.045 + pointer.x * 0.035);",
    "  gl_FragColor = vec4(color * light, 1.0);",
    "}"
  ].join("\n");
  function shader(type, source) {
    const result = gl.createShader(type);
    gl.shaderSource(result, source);
    gl.compileShader(result);
    if (!gl.getShaderParameter(result, gl.COMPILE_STATUS)) {
      gl.deleteShader(result);
      throw new Error("Decorative surface unavailable");
    }
    return result;
  }
  function stop() {
    cancelAnimationFrame(frame);
    frame = 0;
    last = 0;
  }
  function draw() {
    if (!ready || gl.isContextLost()) return;
    gl.useProgram(program);
    gl.uniform2f(gl.getUniformLocation(program, "resolution"), canvas.width, canvas.height);
    gl.uniform2f(gl.getUniformLocation(program, "imageSize"), image.naturalWidth, image.naturalHeight);
    gl.uniform2f(gl.getUniformLocation(program, "pointer"), pointer[0], pointer[1]);
    gl.uniform1f(gl.getUniformLocation(program, "time"), time);
    gl.drawArrays(gl.TRIANGLES, 0, 6);
  }
  function resize() {
    if (!ready) return;
    const bounds = canvas.getBoundingClientRect();
    // Limit resolution and rendering rate for this purely decorative effect.
    const density = Math.min(devicePixelRatio || 1, 1.5, 1800 / Math.max(1, bounds.width));
    canvas.width = Math.max(1, Math.round(bounds.width * density));
    canvas.height = Math.max(1, Math.round(bounds.height * density));
    gl.viewport(0, 0, canvas.width, canvas.height);
    draw();
  }
  function tick(stamp) {
    if (!ready || paused || reduced.matches || !visible || document.hidden || disposed) {
      stop();
      return;
    }
    if (!last || stamp - last >= 1000 / 30) {
      if (last) time += Math.min((stamp - last) / 1000, 0.1);
      last = stamp;
      pointer = pointer.map((value, i) => value + (target[i] - value) * 0.05);
      draw();
    }
    frame = requestAnimationFrame(tick);
  }
  function sync() {
    stop();
    toggle.hidden = !ready || reduced.matches;
    toggle.setAttribute("aria-pressed", String(paused));
    text.textContent = root.dataset.lang === "es"
      ? (paused ? "Reanudar animación" : "Pausar animación")
      : (paused ? "Resume animation" : "Pause animation");
    art.dataset.motion = reduced.matches ? "reduced" : (paused ? "paused" : "running");
    if (reduced.matches) {
      art.dataset.rendered = "false";
    } else if (ready) {
      art.dataset.rendered = "true";
      draw();
      if (!paused && visible && !document.hidden) frame = requestAnimationFrame(tick);
    }
  }
  function init() {
    if (disposed || !image.naturalWidth) return;
    try {
      gl = canvas.getContext("webgl", { alpha: false, antialias: false, depth: false, powerPreference: "low-power" });
      if (!gl) return; // The image is already the complete default fallback.
      const vs = shader(gl.VERTEX_SHADER, vertex), fs = shader(gl.FRAGMENT_SHADER, fragment);
      program = gl.createProgram();
      gl.attachShader(program, vs);
      gl.attachShader(program, fs);
      gl.linkProgram(program);
      gl.deleteShader(vs);
      gl.deleteShader(fs);
      if (!gl.getProgramParameter(program, gl.LINK_STATUS)) throw new Error("Surface unavailable");
      gl.useProgram(program);
      buffer = gl.createBuffer();
      gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
      gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1, 1,-1, -1,1, -1,1, 1,-1, 1,1]), gl.STATIC_DRAW);
      const position = gl.getAttribLocation(program, "position");
      gl.enableVertexAttribArray(position);
      gl.vertexAttribPointer(position, 2, gl.FLOAT, false, 0, 0);
      texture = gl.createTexture();
      gl.bindTexture(gl.TEXTURE_2D, texture);
      gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, gl.RGB, gl.UNSIGNED_BYTE, image);
      gl.uniform1i(gl.getUniformLocation(program, "artwork"), 0);
      ready = true;
      resize();
      sync();
    } catch {
      ready = false;
      art.dataset.rendered = "false";
      toggle.hidden = true;
    }
  }
  root.addEventListener("pointermove", (event) => {
    if (coarse.matches || reduced.matches || paused) return;
    const bounds = root.getBoundingClientRect();
    target = [(event.clientX - bounds.left) / bounds.width * 2 - 1,
      1 - (event.clientY - bounds.top) / bounds.height * 2];
  }, { passive: true });
  root.addEventListener("pointerleave", () => { target = [0, 0]; });
  toggle.addEventListener("click", () => { paused = !paused; sync(); });
  reduced.addEventListener("change", sync);
  document.addEventListener("visibilitychange", sync);
  canvas.addEventListener("webglcontextlost", (event) => {
    event.preventDefault();
    ready = false;
    stop();
    art.dataset.rendered = "false";
    toggle.hidden = true;
  });
  canvas.addEventListener("webglcontextrestored", init);
  const resizeObserver = new ResizeObserver(resize);
  resizeObserver.observe(art);
  const intersectionObserver = new IntersectionObserver(([entry]) => {
    visible = entry.isIntersecting;
    sync();
  });
  intersectionObserver.observe(root);
  window.addEventListener("pagehide", () => {
    disposed = true;
    stop();
    resizeObserver.disconnect();
    intersectionObserver.disconnect();
  });
  window.addEventListener("pageshow", (event) => {
    if (event.persisted) {
      disposed = false;
      resizeObserver.observe(art);
      intersectionObserver.observe(root);
      sync();
    }
  });
  if (image.complete) init();
  else image.addEventListener("load", init, { once: true });
})();
