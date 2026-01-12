document.addEventListener('DOMContentLoaded', async () => {
    urlMethods = `${window.location.origin}/analytics-attack-types/`;
    urlRisc = `${window.location.origin}/analytics-risc-assessments/`;
    urlCountry = `${window.location.origin}/analytics-country-attacks/`;

        // Палитра цветов
    const backgroundColors = [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
        '#9966FF', '#FF9F40', '#C9CBCF', '#4D5360',
        '#46BFBD', '#FDB45C', '#00008B'
    ];

    // Заполняем поле select Министерствами
    const getDepartments = async () => {
        url = `${window.location.origin}/get_departments/`;
        const selectInput = document.querySelector('#counrties-for-select');
        const result = await fetch(url);
        const departments = await result.json();
        departments.forEach(name_array => {
            const [name_en, name_ru, id] = name_array;
            const name = name_ru ? `${name_en} ${name_ru}` : name_en;
            const option = document.createElement('option');
            option.value = id;
            option.textContent = name;

            selectInput.appendChild(option);
        });
    };
    getDepartments();

    const getdata = async (url, department=null, start=null, end=null) => {
        const urlObject = new URL(url);
        if (department) urlObject.searchParams.append('department', department);

        if (start && end) {
            urlObject.searchParams.append("start", start);
            urlObject.searchParams.append("end", end);
        }
        const result = await fetch(urlObject);
        const data = await result.json();
        return data;
    };

    // график методов атак
    const fillChart = async (canvasEl, chartLabels, chartData) => {
        // Инициализация диаграммы
        const ctx = canvasEl.getContext('2d');
        const chart = new Chart(ctx, {
            type: 'pie',
            data: {
              labels: chartLabels,
              datasets: [{
                data: chartData,
                backgroundColor: backgroundColors,
                label: 'Процент от общего числа атак'
              }]
        },
        options: {
          responsive: true,
          plugins: {
            tooltip: {
              callbacks: {
                label: ctx => ctx.label + ': ' + ctx.parsed + '%'
              }
            },
            legend: { display: false }
          }
        }
        });
        return chart;
    };

    // заполняет список под граффиком
    const fillLabels = async (legendContainer, chartLabels, chartData, countList=null) => {
        // Генерация пользовательской легенды
        legendContainer.innerHTML = '';
        chartLabels.forEach((label, i) => {
            const li = document.createElement('li');
            li.innerHTML =
              `<span style="display:inline-block;width:12px;height:12px;background-color:${backgroundColors[i]};margin-right:8px;"></span>` +
              `${label} — ${chartData[i]}% - ${countList[i]}`;
            legendContainer.appendChild(li);
        });
    };

    // есть два граффика: один для методов атак, второй по рискам атак
    let methodChart = null;  // глобальная переменная
    const methodCanvas = document.getElementById('attack-methods-chart');
    const legendContainer = document.getElementById('legend');

    let riscChart = null;
    const riscCanvas = document.getElementById('attack-risc-chart');
    const riscLegend = document.getElementById('legend-risc');

    const updateMethodsChart = async (department, start=null, end=null) => {
        const data = await getdata(urlMethods, department, start, end);
        const chartLabels = data.labels;
        const reportCounts = data.data;
        const total = data.total;
        const chartData = reportCounts.map(report => Math.floor(report / total * 100));

        if (chartLabels.length > reportCounts.length) {
            reportCounts.push(Math.floor(chartData.slice(-1) / total * 100));
        }

        await fillLabels(legendContainer, chartLabels, chartData, reportCounts);

        if (methodChart) {
            methodChart.data.labels = chartLabels;
            methodChart.data.datasets[0].data = chartData;
            methodChart.update();
            return
        }
        methodChart = await fillChart(methodCanvas, chartLabels, chartData);
    };

    const updateRiscChar = async (department, start=null, end=null) => {
        const data = await getdata(urlRisc, department, start, end);
        const chartLabels = data.labels;
        const reportCounts = data.data;
        const total = data.total;
        const chartData = reportCounts.map(report => Math.floor(report / total * 100));

        if (chartLabels.length > reportCounts.length) {
            reportCounts.push(Math.floor(chartData.slice(-1) / total * 100));
        }
        await fillLabels(riscLegend, chartLabels, chartData, reportCounts);

        if (riscChart) {
            riscChart.data.labels = chartLabels;
            riscChart.data.datasets[0].data = chartData;
            riscChart.update();
            return
        }
        riscChart = await fillChart(riscCanvas, chartLabels, chartData);
    }

    // Страны
    let countryChart = null;
    const countryCanvas = document.getElementById('countries-chart');
    const countryLegend = document.getElementById('legend-countries');

    const updateCountryCharts = async (department, start=null, end=null) => {
        const regionNames = new Intl.DisplayNames(['ru'], { type: 'region' });

        const data = await getdata(urlCountry, department, start, end);
        const chartLabels = data.labels.map(code => {
            try {
                return regionNames.of(code.toUpperCase());
            } catch {
                return code ? code.toUpperCase() : 'не указана';
            }
        });

        const reportCounts = data.data;
        const total = data.total;
        const chartData = reportCounts.map(report => Math.floor(report / total * 100));

        if (chartLabels.length > reportCounts.length) {
            reportCounts.push(Math.floor(chartData.slice(-1) / total * 100));
        }

        await fillLabels(countryLegend, chartLabels, chartData, reportCounts);

        if (countryChart) {
            countryChart.data.labels = chartLabels;
            countryChart.data.datasets[0].data = chartData;
            countryChart.update();
            return
        }
        countryChart = await fillChart(countryCanvas, chartLabels, chartData);
    };

    const getIpCount = async (department, start=null, end=null) => {
        const ulr = `${window.location.origin}/analytics-ip-counts/`;
        const data = await getdata(ulr, department, start, end);
        const ipObjects = data.data;
        const total = document.querySelector('#ip-count');
        total.innerText = data.total;

        const table = document.querySelector('#ip-count-table');
        const tableBody = table.querySelector('tbody');
        tableBody.innerHTML = '';

        const fragment = document.createDocumentFragment();
        const regionNames = new Intl.DisplayNames(['ru'], { type: 'region' });
        const ipList =  Object.keys(ipObjects);
        for (const ip of ipList) {
            const tr = document.createElement('tr');
            let column = ``;
            ipObjects[ip].forEach(countryCount => {
                let countryName = '';
                const code = countryCount[0];
                try {
                    countryName = regionNames.of(code.toUpperCase());
                } catch {
                    countryName = code ? code.toUpperCase() : 'не указана';
                }

                column += `<p>${countryName} ${countryCount[1]}</p>`
            });
            tr.innerHTML = `<td>${ip}</td><td>${column}</td>`
            fragment.appendChild(tr);
        }

        tableBody.appendChild(fragment); // Обновляем DOM всего один раз
    };


    const updatePage = async (department=null, start=null, end=null) => {
        await updateMethodsChart(department, start, end);
        await updateRiscChar(department, start, end);
        await updateCountryCharts(department, start, end);
        await getIpCount(department, start, end);
    }
    await updatePage();

    const form = document.querySelector('#reports_filter');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const department = form.elements.department.value === 'all' ? null : form.elements.department.value;
        const start = form.elements.start.value;
        const end = form.elements.end.value;
        await updatePage(department, start, end);
    });
});
