document.addEventListener('DOMContentLoaded', async () => {
    urlMethods = `${window.location.origin}/analytics-attack-types/`;
    urlRisc = `${window.location.origin}/analytics-risc-assessments/`;
    urlCountry = `${window.location.origin}/analytics-country-attacks/`;

        // Палитра цветов
    const backgroundColors = [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
        '#9966FF', '#FF9F40', '#C9CBCF', '#4D5360',
        '#46BFBD', '#FDB45C'
    ].slice(0, 10);

    const getdata = async (url, start=null, end=null) => {
        const urlObject = new URL(url);
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
        const chart = methodChart = new Chart(ctx, {
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

    const fillLabels = async (legendContainer, chartLabels, chartData) => {
        // Генерация пользовательской легенды
        legendContainer.innerHTML = '';
        chartLabels.forEach((label, i) => {
            const li = document.createElement('li');
            li.innerHTML =
              `<span style="display:inline-block;width:12px;height:12px;background-color:${backgroundColors[i]};margin-right:8px;"></span>` +
              `${label} — ${chartData[i]}%`;
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

    const updateMethodsChart = async (start=null, end=null) => {
        const data = await getdata(urlMethods, start, end);
        const chartLabels = data.labels;
        const chartData = data.data;
        await fillLabels(legendContainer, chartLabels, chartData);

        if (methodChart) {
            methodChart.data.labels = chartLabels;
            methodChart.data.datasets[0].data = chartData;
            methodChart.update();
            return
        }
        methodChart = await fillChart(methodCanvas, chartLabels, chartData);
    };

    const updateRiscChar = async (start=null, end=null) => {
        const data = await getdata(urlRisc, start, end);
        const chartLabels = data.labels;
        const chartData = data.data;
        await fillLabels(riscLegend, chartLabels, chartData);

        if (riscChart) {
            riscChart.data.labels = chartLabels;
            riscChart.data.datasets[0].data = chartData;
            riscChart.update();
            return
        }
        riscChart = await fillChart(riscCanvas, chartLabels, chartData);
    }

    let countryChart = null;
    const countryCanvas = document.getElementById('countries-chart');
    const countryLegend = document.getElementById('legend-countries');

    const updateCountryCharts = async (start=null, end=null) => {
        const data = await getdata(urlCountry, start, end);
        const chartLabels = data.labels;
        const chartData = data.data;
        await fillLabels(countryLegend, chartLabels, chartData);

        if (countryChart) {
            countryChart.data.labels = chartLabels;
            countryChart.data.datasets[0].data = chartData;
            countryChart.update();
            return
        }
        countryChart = await fillChart(countryCanvas, chartLabels, chartData);
    };


    const updatePage = async (start=null, end=null) => {
        await updateMethodsChart(start, end);
        await updateRiscChar(start, end);
        await updateCountryCharts(start, end)
    }
    await updatePage();

    const form = document.querySelector('#reports_filter');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const start = form.elements.start.value;
        const end = form.elements.end.value;
        await updatePage(start, end);
    });
});
