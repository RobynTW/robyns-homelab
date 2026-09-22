setTimeout(() => {
  document.querySelectorAll("#services > .services-group").forEach(group => {
    const name = group.querySelector("h2")?.textContent.trim();

    if (name === "Gaming") group.classList.add("service-group-gaming");
    if (name === "Monitoring") group.classList.add("service-group-monitoring");
    if (name === "Network") group.classList.add("service-group-network");
  });

  const github = document.querySelector("#widgets-wrap > .information-widget-logo");

  if (!github || document.querySelector("#frieren-gif")) return;

  const size = github.getBoundingClientRect();

  const gif = document.createElement("img");

  gif.id = "frieren-gif";
  gif.src = "/images/frieren-spinning.gif";
  gif.alt = "Frieren spinning";
  gif.width = size.width;
  gif.height = size.height;

  Object.assign(gif.style, {
    width: `${size.width}px`,
    height: `${size.height}px`,
    objectFit: "contain",
    display: "block",
    flexShrink: "0",
    marginLeft: "0.75rem"
  });

  github.insertAdjacentElement("afterend", gif);
}, 1000);