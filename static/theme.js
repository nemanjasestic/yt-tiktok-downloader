document.addEventListener("DOMContentLoaded", () => {
  const button = document.getElementById("themeToggle");
  const html = document.documentElement;

  const stored = localStorage.getItem("theme");
  if (stored === "light") {
    html.classList.remove("dark");
    html.classList.add("light");
    html.setAttribute("data-theme", "light");
  } else {
    html.classList.remove("light");
    html.classList.add("dark");
    html.setAttribute("data-theme", "dark");
  }

  button.addEventListener("click", () => {
    const isDark = html.getAttribute("data-theme") === "dark";
    const newTheme = isDark ? "light" : "dark";
    html.classList.toggle("dark", !isDark);
    html.classList.toggle("light", isDark);
    html.setAttribute("data-theme", newTheme);
    localStorage.setItem("theme", newTheme);
  });
});
