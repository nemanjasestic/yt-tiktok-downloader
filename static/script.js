const form = document.getElementById("download-form");
const qualitySelect = document.getElementById("quality");
const inlineAd = document.getElementById("inline-ad");
const skipInlineAd = document.getElementById("skip-inline-ad");
const downloadBtn = document.getElementById("download-btn");

form.addEventListener("submit", function (e) {
  if (qualitySelect.value === "1080p") {
    e.preventDefault(); // stopuj submit dok se ne odgleda reklama
    showInlineAd(() => {
      form.submit(); // nastavi posle reklame
    });
  }
});

function showInlineAd(callback) {
  inlineAd.classList.remove("hidden");
  let seconds = 5;
  skipInlineAd.innerText = `You can skip in ${seconds}s`;
  skipInlineAd.disabled = true;

  const timer = setInterval(() => {
    seconds--;
    skipInlineAd.innerText = seconds > 0 ? `You can skip in ${seconds}s` : "Skip";
    if (seconds <= 0) {
      skipInlineAd.disabled = false;
      clearInterval(timer);
    }
  }, 1000);

  skipInlineAd.onclick = () => {
    inlineAd.classList.add("hidden");
    callback(); // pokreni pravi download
  };
}
