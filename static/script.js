async function fetchCrypto() {
    try {
        const response = await fetch(
            'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1'
        );
        const data = await response.json();

        const tableBody = document.getElementById('crypto-table');
        tableBody.innerHTML = '';

        data.forEach((coin, index) => {
            const change = coin.price_change_percentage_24h.toFixed(2);
            const isPositive = change >= 0;

            tableBody.innerHTML += `
                <tr>
                    <td>${index + 1}</td>
                    <td>
                        <img src="${coin.image}" width="25" style="vertical-align:middle; margin-right:8px;">
                        ${coin.name} (${coin.symbol.toUpperCase()})
                    </td>
                    <td>$${coin.current_price.toLocaleString()}</td>
                    <td class="${isPositive ? 'positive' : 'negative'}">
                        ${isPositive ? '▲' : '▼'} ${Math.abs(change)}%
                    </td>
                    <td>$${(coin.market_cap / 1e9).toFixed(2)}B</td>
                </tr>
            `;
        });
    } catch (error) {
        document.getElementById('crypto-table').innerHTML = 
            '<tr><td colspan="5">Error loading data. Try again!</td></tr>';
    }
}

fetchCrypto();
setInterval(fetchCrypto, 30000);