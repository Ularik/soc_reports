document.querySelector('#static-report-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const form = e.target;
    const params = new URLSearchParams(new FormData(form)).toString();
    const url = `${window.location.origin}/analytics-static-reports/`;

    const response = await fetch(url);

    if (!response.ok) throw new Error("Ошибка при получении данных");

    const reportData = await response.json();
    const { reports, file } = reportData;

    // Декодируем base64 и создаём файл
    const byteCharacters = atob(file.content);
    const byteNumbers = new Uint8Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const blob = new Blob([byteNumbers], { type: file.content_type });

    // Создаём ссылку для скачивания
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = file.filename;
    link.click();
    URL.revokeObjectURL(link.href);

    // заполняем таблицу на странице
    const tbody = document.getElementById("reportBody");

    console.log(reports);
    Object.entries(reports).forEach(([surname, depts], index) => {
      const tr = document.createElement("tr");

      // Базовые столбцы: №, ФИО, Проанализированные правила
      tr.innerHTML = `
        <td>${index + 1}</td>
        <td>${surname}</td>
        <td></td>
      `;

      // Порядок ведомств — как в заголовке таблицы
      const order = {
          'MF': 'МФ',
          'SCS': 'ГТС',
          'TAX': 'ГНС',
          'GP': 'ГП "Инфоком"',
          'MID': 'МИД',
          'PEO': 'УДП КР'
      };

      Object.keys(order).forEach(depID => {
        console.log(depID, depts[depID]);
        const h = depts[depID]?.Высокая ?? 0;
        let m = depts[depID]?.Средняя ?? 0;
        m += depts[depID]?.Низкая ?? 0;
        tr.innerHTML += `<td>${h}</td><td>${m}</td>`;
      });

      // IRP — Ложные срабатывания
      tr.innerHTML += `<td>0</td>`; // Лож

      // СФ
      tr.innerHTML += `<td>0</td><td>0</td>`;

      // ФОМ
      tr.innerHTML += `<td>0</td><td>0</td>`;

      tbody.appendChild(tr);
      console.log(tbody);
    });
});