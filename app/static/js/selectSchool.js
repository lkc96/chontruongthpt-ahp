document.addEventListener("DOMContentLoaded", () => {
  const selects = document.querySelectorAll(".truong-select");
  const loaiTruongSelect = document.getElementById("loai-truong");

  function filterSchoolsByType() {
    const selectedLoaiTruong = loaiTruongSelect.value;

    selects.forEach(select => {
      const options = select.querySelectorAll("option");

      options.forEach(option => {
        // Trường hợp option mặc định hoặc chưa chọn loại trường thì hiển thị
        if (option.value === "" || !option.dataset.loai) {
          option.hidden = false;
          return;
        }

        // Ẩn nếu không đúng loại trường
        option.hidden = (option.dataset.loai !== selectedLoaiTruong);
      });
    });

    updateOptions();  // Cập nhật để không bị trùng trường
  }

  function updateOptions() {
    const selectedValues = Array.from(selects).map(s => s.value);

    selects.forEach(select => {
      const currentValue = select.value;
      const options = select.querySelectorAll("option");

      options.forEach(option => {
        if (option.value === "" || option.value === currentValue) {
          option.hidden = false;
        } else if (selectedValues.includes(option.value)) {
          option.hidden = true;
        }
      });
    });
  }

  selects.forEach(select => {
    select.addEventListener("change", updateOptions);
  });

  loaiTruongSelect.addEventListener("change", filterSchoolsByType);

  filterSchoolsByType();  // Gọi khi load trang
});

function submitSelectedSchools() {
  const selectedIds = [];
  for (let i = 0; i < 5; i++) {
    const select = document.getElementById(`truong-select-${i}`);
    if (select.value) {
      selectedIds.push(select.value);
    }
  }

  if (selectedIds.length !== 5) {
    alert("Vui lòng chọn đủ 5 trường!");
    return;
  }

  fetch("/get_school_info", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ truong_ids: selectedIds })
  })
  .then(res => res.json())
  .then(data => {
    const resultBody = document.getElementById("resultBody");
    resultBody.innerHTML = "";
  
    data.truongs.forEach((item, index) => {
      const row = `<tr>
        <td>Phương án ${index + 1}</td>
        <td>${item.ten_truong}</td>
      </tr>`;
      resultBody.innerHTML += row;
    });
  
    console.log("Ma trận chất lượng giáo dục:", data.matrix_clgd);
    console.log("Ma trận cơ sở vật chất:", data.matrix_csvc);
    console.log("Ma trận hoạt động:", data.matrix_hd);
    console.log("Ma trận học phí:", data.matrix_hp);
  });
}

function openAHPMatrices() {
  const selectedIds = [];
  for (let i = 0; i < 5; i++) {
    const select = document.getElementById(`truong-select-${i}`);
    if (select.value) {
      selectedIds.push(select.value);
    }
  }

  if (selectedIds.length !== 5) {
    alert("Vui lòng chọn đủ 5 trường!");
    return;
  }
  fetch("/ahp_matrices", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ truong_ids: selectedIds })  // bạn phải đảm bảo selectedIds tồn tại
  })
  .then(res => res.text())
  .then(html => {
    const w = window.open();
    w.document.write(html);
  });
}

function getCriteriaMatrix() {
  const size = criteria.length;
  const matrix = [];

  for (let i = 0; i < size; i++) {
    const row = [];
    for (let j = 0; j < size; j++) {
      let value;
      if (i === j) {
        value = 1;
      } else if (j > i) {
        const input = document.getElementById(`cell-${i}-${j}`);
        const raw = input.value.trim();
        value = parseFraction(raw);  // dùng lại hàm bạn đã định nghĩa
      } else {
        const input = document.getElementById(`cell-${i}-${j}`);
        value = parseFraction(input.value.trim());
      }
      row.push(value);
    }
    matrix.push(row);
  }

  return matrix;
}

function submitAHPMatrix() {
  const matrix = getCriteriaMatrix();

  const selectedIds = [];
  for (let i = 0; i < 5; i++) {
    const select = document.getElementById(`truong-select-${i}`);
    if (select.value) {
      selectedIds.push(select.value);
    }
  }

  if (selectedIds.length !== 5) {
    alert("Vui lòng chọn đủ 5 trường!");
    return;
  }
  fetch("/ahp_calculate_final", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      criteria_matrix: matrix,
      truong_ids: selectedIds
    })
  })
  .then(response => response.json())
  .then(result => {
    console.log("Kết quả cuối cùng:", result);

    const results = result.results;
    // Sắp xếp kết quả theo điểm giảm dần
    results.sort((a, b) => b.diem - a.diem);

    const tableBody = document.getElementById("ahp-results-body");
    tableBody.innerHTML = ""; // Reset bảng kết quả cũ

    // Lặp qua kết quả để hiển thị vào bảng
    results.forEach((item, index) => {
      const row = document.createElement("tr");

      const rankCell = document.createElement("td");
      rankCell.textContent = index + 1;

      const nameCell = document.createElement("td");
      nameCell.textContent = item.ten_truong;

      const scoreCell = document.createElement("td");
      scoreCell.textContent = item.diem.toFixed(4); // Làm tròn điểm đến 4 chữ số

      row.appendChild(rankCell);
      row.appendChild(nameCell);
      row.appendChild(scoreCell);

      tableBody.appendChild(row);
    });
    // 👉 Trực quan hóa bằng biểu đồ cột
const chartLabels = results.map(r => r.ten_truong);
const chartData = results.map(r => r.diem);

// Xóa biểu đồ cũ nếu đã có
if (window.ahpRankingChart instanceof Chart) {
  window.ahpRankingChart.destroy();
}

// Vẽ biểu đồ mới
const ctx = document.getElementById("ahpRankingChart").getContext("2d");
window.ahpRankingChart = new Chart(ctx, {
  type: 'bar',
  data: {
    labels: chartLabels,
    datasets: [{
      label: "Điểm xếp hạng",
      data: chartData,
      backgroundColor: "rgba(30, 74, 50, 1)",
      borderColor: "rgba(30, 74, 50, 1)",
      borderWidth: 1
    }]
  },
  options: {
    responsive: true,
    scales: {
      y: {
        beginAtZero: true,
        max: 0.4
      }
    },
    plugins: {
      legend: {
        display: true
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            return `Điểm: ${context.raw.toFixed(4)}`;
          }
        }
      }
    }
  }
});
    // Hiển thị bảng kết quả
    document.getElementById("ahp-results").style.display = "block"; // Mở bảng kết quả
  })
  .catch(error => {
    console.error("Lỗi khi gửi ma trận:", error);
  });
}