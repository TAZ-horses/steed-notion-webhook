<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Steed Media Mindmap</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <script src="https://d3js.org/d3.v7.min.js"></script>
  <style>
    html, body {
      margin: 0;
      padding: 0;
      overflow: hidden;
      font-family: 'Instrument Sans', sans-serif;
      background: #f4f4f4;
    }
    #mindmap {
      width: 100vw;
      height: 100vh;
    }
    .node circle {
      stroke: #fff;
      stroke-width: 2px;
    }
    .node text {
      font-size: 12px;
      fill: #2a423f;
      user-select: none;
    }
    .link {
      fill: none;
      stroke: #bbb;
      stroke-opacity: 0.5;
      stroke-width: 1.5px;
    }
    .tooltip {
      position: absolute;
      background: #fff;
      border: 1px solid #ccc;
      padding: 10px;
      font-size: 13px;
      pointer-events: none;
      display: none;
      z-index: 10;
      max-width: 300px;
      border-radius: 8px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    #toolbar {
      position: fixed;
      top: 10px;
      right: 10px;
      background: #ffffffcc;
      backdrop-filter: blur(8px);
      border: 1px solid #ccc;
      padding: 10px;
      border-radius: 8px;
      z-index: 100;
      font-size: 14px;
      display: flex;
      gap: 10px;
    }
    #toolbar button {
      background: #2a423f;
      color: white;
      border: none;
      padding: 6px 10px;
      border-radius: 4px;
      cursor: pointer;
    }
    #toolbar button:hover {
      background: #ee0505;
    }
    .copy-btn {
      background: none;
      border: none;
      cursor: pointer;
      margin-left: 5px;
      font-size: 12px;
      padding: 2px 5px;
      border-radius: 3px;
      background: #f0f0f0;
    }
    .copy-btn:hover {
      background: #ddd;
    }
  </style>
</head>
<body>
  <svg id="mindmap"></svg>
  <div id="tooltip" class="tooltip"></div>
  <div id="toolbar">
    <button onclick="toggleAllPasswords()">🔓 Toggle Passwords</button>
    <button onclick="exportAsPNG()">📷 Export Map</button>
    <button onclick="location.reload()">🔄 Reload</button>
  </div>

  <script>
    // Updated to match your data categories
    const colorMap = {
      "business tools": "#2a423f",
      "Hosting": "#ee0505",
      "development": "#007bff",
      "social media": "#f39c12"
    };

    const iconMap = {
      "business tools": "💼",
      "Hosting": "🌐",
      "development": "💻",
      "social media": "📱"
    };

    const width = window.innerWidth;
    const height = window.innerHeight;
    const radius = Math.min(width, height) / 2.2;

    const container = d3.select("#mindmap")
      .attr("width", width)
      .attr("height", height);

    const svg = container.append("g")
      .attr("transform", `translate(${width / 2}, ${height / 2})`);

    container.call(d3.zoom().scaleExtent([0.5, 4]).on("zoom", (e) => {
      svg.attr("transform", e.transform);
    }));

    const tooltip = d3.select("#tooltip");

    let allPasswordsVisible = false;

    function toggleAllPasswords() {
      allPasswordsVisible = !allPasswordsVisible;
      document.querySelectorAll(".password-field").forEach(span => {
        span.textContent = allPasswordsVisible ? span.dataset.pass : "••••••";
      });
      const toggleBtn = document.querySelector("#toolbar button:first-child");
      toggleBtn.textContent = allPasswordsVisible ? "🔒 Hide Passwords" : "🔓 Show Passwords";
    }

    function exportAsPNG() {
      const svgEl = document.getElementById("mindmap");
      const svgData = new XMLSerializer().serializeToString(svgEl);
      const canvas = document.createElement("canvas");
      canvas.width = width;
      canvas.height = height;
      const ctx = canvas.getContext("2d");
      const img = new Image();
      img.onload = function () {
        ctx.drawImage(img, 0, 0);
        const png = canvas.toDataURL("image/png");
        const link = document.createElement("a");
        link.download = "steed_mindmap.png";
        link.href = png;
        link.click();
      };
      img.src = "data:image/svg+xml;base64," + btoa(unescape(encodeURIComponent(svgData)));
    }

    function renderMindmap(data) {
      const root = {
        name: "Steed Media",
        children: Object.entries(data).map(([category, services]) => ({
          name: category,
          color: colorMap[category] || "#888",
          icon: iconMap[category] || "📁",
          children: services.map(s => ({
            name: s.service,
            description: s.description,
            username: s.username,
            password: s.password,
            notes: s.notes
          }))
        }))
      };

      const rootNode = d3.hierarchy(root);
      const tree = d3.tree().size([2 * Math.PI, radius]);
      tree(rootNode);

      svg.selectAll(".link")
        .data(rootNode.links())
        .join("path")
        .attr("class", "link")
        .attr("d", d3.linkRadial()
          .angle(d => d.x)
          .radius(d => d.y)
        );

      const node = svg.selectAll(".node")
        .data(rootNode.descendants())
        .join("g")
        .attr("class", "node")
        .attr("transform", d => `rotate(${(d.x * 180 / Math.PI - 90)}) translate(${d.y},0)`);

      node.append("circle")
        .attr("r", 5)
        .attr("fill", d => d.data.color || "#2a423f");

      node.append("text")
        .attr("dy", "0.31em")
        .attr("x", d => d.x < Math.PI === !d.children ? 10 : -10)
        .attr("text-anchor", d => d.x < Math.PI === !d.children ? "start" : "end")
        .attr("transform", d => d.x >= Math.PI ? "rotate(180)" : null)
        .text(d => `${d.data.icon || ""} ${d.data.name}`)
        .append("title")
        .text(d => d.data.name);

      node.on("click", (event, d) => {
        if (d.data.username || d.data.password || d.data.notes || d.data.description) {
          const passwordContent = d.data.password 
            ? `<b>Pass:</b> <span class="password-field" data-pass="${d.data.password}">••••••</span>
               <button class="copy-btn">📋</button><br>`
            : "";

          tooltip.style("display", "block")
            .html(`
              <strong>${d.data.name}</strong><br>
              ${d.data.description ? `<em>${d.data.description}</em><br>` : ""}
              ${d.data.username ? `<b>User:</b> ${d.data.username}<br>` : ""}
              ${passwordContent}
              ${d.data.notes ? `<b>Notes:</b> ${d.data.notes}` : ""}
            `)
            .style("left", (event.pageX + 10) + "px")
            .style("top", (event.pageY - 20) + "px");

          // Add click handler for copy button
          if (d.data.password) {
            tooltip.select(".copy-btn").on("click", function() {
              navigator.clipboard.writeText(d.data.password)
                .then(() => {
                  this.textContent = "✓";
                  setTimeout(() => this.textContent = "📋", 1000);
                });
            });
          }
        }
      });

      svg.on("click", () => tooltip.style("display", "none"));
    }

    fetch("mindmap_data.json")
      .then(res => res.json())
      .then(renderMindmap)
      .catch(err => {
        console.error("Mindmap fetch failed:", err);
        d3.select("body").append("div")
          .style("color", "red")
          .style("padding", "20px")
          .html("<h2>Error loading mindmap data.</h2>");
      });
  </script>
</body>
</html>
