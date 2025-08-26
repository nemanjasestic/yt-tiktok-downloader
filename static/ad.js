function showAd(onClose) {
  const adOverlay = document.createElement("div");
  adOverlay.className = "fixed inset-0 bg-black bg-opacity-80 z-50 flex items-center justify-center";
  adOverlay.innerHTML = `
    <div class="bg-white dark:bg-gray-800 text-center p-6 rounded-xl shadow-lg max-w-sm mx-auto">
      <h2 class="text-xl font-semibold mb-4 dark:text-white">Watch this short ad to download in 1080p</h2>
      <video autoplay muted loop class="w-full rounded mb-4">
        <source src="https://www.w3schools.com/html/mov_bbb.mp4" type="video/mp4">
      </video>
      <button id="closeAd" class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded">Skip Ad</button>
    </div>
  `;
  document.body.appendChild(adOverlay);
  setTimeout(() => {
    document.getElementById('closeAd').disabled = false;
  }, 5000);

  document.getElementById('closeAd').onclick = () => {
    adOverlay.remove();
    if (onClose) onClose();
  };
}
