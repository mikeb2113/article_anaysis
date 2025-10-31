//const POLYGON_API_KEY = 'PPXHHyGGaXZW2NG_YABBjr4RrZ9FIRHT'; // Replace with your actual Polygon.io API key
//const ALPHA_VANTAGE_API_KEY = 'BQJFR4W9ZYTKDUYL'; // Replace with your actual Alpha Vantage API key
//financialmodelingprep API key = '4zRGoPkgudUC05HW8kPh3qr8QE198tKh'

//Polygon rate limit: 5 requests per minute
//Alpha vantage rate limit: 25 requests per day
//Default to using the polygon api for standard requests, and include an exception so that
//in the event that polygon is in the 5 minute window, then it will fall back to the vantage api
//vantage isn't ideal because of the duration of the rate limit, but can be useful for padding the gaps of better APIs
//Vantage also includes an addition 5 minute delay in the same vein as polygon, so be aware. A third key may be useful/needed if this becomes
//an issue/if this scales well
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import { Line } from 'react-chartjs-2';
import 'chart.js/auto';

const fetchStockData = async (ticker) => {
  try {
    // Replace `/api/quote` with the actual API endpoint
    const response = await axios.get(`https://financialmodelingprep.com/api/v3/quote/${ticker}?apikey=4zRGoPkgudUC05HW8kPh3qr8QE198tKh`);
    
    // Assuming the response structure from the API returns a list
    const stockInfo = response.data[0]; // Access the first object in the response array
    
    const data = {
      longName: stockInfo.name || ticker, // Use name if available, else fallback to ticker
      symbol: stockInfo.symbol,
      regularMarketPrice: stockInfo.price,
      regularMarketPreviousClose: stockInfo.previousClose,
      regularMarketOpen: stockInfo.open,
      regularMarketDayHigh: stockInfo.dayHigh,
      regularMarketDayLow: stockInfo.dayLow,
    };

    console.log(data); // Log data for debugging
    return data;
  } catch (error) {
    console.error('Error fetching the stock data', error);
    throw new Error('Error fetching the stock data');
  }
};

const fetchHistoricalData = async (ticker, rangeValue, rangeUnit) => {
  try {
    // Set resolution/interval based on the range unit
    let resolution;
    switch (rangeUnit) {
      case 'days':
        resolution = '1d';  // API specific format for 1 day intervals
        break;
      case 'months':
        resolution = '1mo'; // API specific format for 1 month intervals
        break;
      case 'years':
        resolution = '1y';  // API specific format for 1 year intervals
        break;
      default:
        resolution = '1d';  // Default to daily data
    }

    // Calculate start and end dates in the correct format (YYYY-MM-DD)
    const endDate = new Date(); // Current date
    let startDate = new Date();

    // Adjust the start date based on the selected range unit
    switch (rangeUnit) {
      case 'days':
        startDate.setDate(endDate.getDate() - rangeValue);
        break;
      case 'months':
        startDate.setMonth(endDate.getMonth() - rangeValue);
        break;
      case 'years':
        startDate.setFullYear(endDate.getFullYear() - rangeValue);
        break;
      default:
        startDate.setDate(endDate.getDate() - rangeValue);
    }

    // Format dates as 'YYYY-MM-DD'
    const period1 = startDate.toISOString().split('T')[0];
    const period2 = endDate.toISOString().split('T')[0];

    // Make the request to fetch historical data
    const response = await axios.get(
      `https://financialmodelingprep.com/api/v3/historical-price-full/${ticker}?from=${period1}&to=${period2}&serietype=line&apikey=4zRGoPkgudUC05HW8kPh3qr8QE198tKh`
    );
    
    // Ensure that the response has the correct data structure
    const historicalData = response.data.historical;
    
    if (!historicalData || historicalData.length === 0) {
      throw new Error('No historical data available');
    }

    // Map the historical data to chart-friendly format
    const data = historicalData.map(entry => ({
      date: new Date(entry.date).toISOString().split('T')[0], // Extract date
      price: entry.close, // Extract closing price
    }));

    // Sort data by ascending date
    data.sort((a, b) => new Date(a.date) - new Date(b.date));

    // Extract sorted labels and prices
    const labels = data.map(entry => entry.date);
    const prices = data.map(entry => entry.price);

    return { labels, prices };
  } catch (error) {
    console.error('Error fetching the historical stock data', error);
    throw new Error('Error fetching the historical stock data');
  }
};

function StockInfoComponent({
  error,
  stockData,
  chartData,
  rangeValue,
  setRangeValue,
  rangeUnit,
  setRangeUnit,
}) {
  return (
    <>
      {error && <p style={{ color: 'red' }}>{error}</p>}

      {stockData && (
        <div>
          <h2>
            {stockData.longName} ({stockData.symbol})
          </h2>
          <p>Price: {stockData.regularMarketPrice}</p>
          <p>Open: {stockData.regularMarketOpen}</p>
          <p>High: {stockData.regularMarketDayHigh}</p>
          <p>Low: {stockData.regularMarketDayLow}</p>
        </div>
      )}

      {chartData && (
        <div style={{ width: '80%', height: '400px' }}>
          <Line data={chartData} options={{ maintainAspectRatio: false }} />
        </div>
      )}

      <div id="range-header-component">
        <label id="range">
          Range:
          <input
            type="number"
            value={rangeValue}
            onChange={(e) => setRangeValue(Number(e.target.value))}
            min="1"
          />
        </label>
        <label>
          Unit:
          <select
            value={rangeUnit}
            onChange={(e) => setRangeUnit(e.target.value)}
          >
            <option value="days">Days</option>
            <option value="months">Months</option>
            <option value="years">Years</option>
          </select>
        </label>
      </div>
    </>
  );
}

function LoadScreen() {
  const [factoidCount, setFactoidCount] = useState(1);
  const [factoids, setFactoids] = useState([
    "On October 19, 1987, also known as Black Monday, the Dow Jones Industrial Average fell by 22.6%—the biggest one-day percentage drop in history.",
  ]);

  // Predefined list of factoids
  const factoidList = [
    "The Amsterdam Stock Exchange, founded in 1602, is the world's oldest stock exchange.",
    "The New York Stock Exchange is the largest in the world, with a market cap over $28 trillion.",
    "The first publicly traded stock was the Dutch East India Company in 1602.",
    "Warren Buffett bought his first stock at age 11. Today, Berkshire Hathaway shares are worth hundreds of thousands of dollars!",
    "Apple’s stock price was $1.36 per share in 2001. Now it’s one of the highest-valued companies in the world!",
    "Wall Street got its name from a wall built by the Dutch in the 17th century.",
    "If you can't afford to lose it, you shouldn't invest it!",
    "Some companies try to get creative or meaningful stock ticker symbols. For example, Harley-Davidson's stock ticker is \"HOG,\" while Southwest Airlines is \"LUV.\"",
    "The opening bell of the New York Stock Exchange rings at exactly 9:30 AM EST every weekday. The first time a bell was used to open trading was in the 1870s.",
    "The fastest bear market decline in history happened in 2020 when the market fell over 20% in just 16 days due to the global COVID-19 pandemic.",
    "On its first day of trading in 1896, the Dow Jones Industrial Average closed at 40.94. Now it regularly trades over 30,000!",
    "The New York Stock Exchange traces its origins to 1792 when 24 brokers signed the Buttonwood Agreement under a buttonwood tree on Wall Street.",
    "If you had invested $1,000 in Warren Buffett's company, Berkshire Hathaway, when he took over in 1964, it would be worth over $88 million today!",
    "The longest bull market in history lasted 11 years, from March 2009 until February 2020, without experiencing a 20% or greater decline.",
    "Tesla became one of the most valuable companies in the world within just 17 years of its initial public offering (IPO) in 2010, surpassing many legacy automakers that have been around for over 100 years.",
    "There’s a stock market superstition called the “Super Bowl Indicator.” It claims that if a team from the National Football Conference (NFC) wins the Super Bowl, the stock market will go up that year, and if an American Football Conference (AFC) team wins, the market will fall.",
    "A Company's Lifespan: On average, a company in the S&P 500 is expected to remain in the index for 15-20 years. In 1958, the average was 61 years.",
    "Apple became the first company in history to reach a $1 trillion market valuation in 2018, then surpassed $2 trillion in 2020.",
    "As more companies list on stock exchanges, creative and concise ticker symbols are becoming harder to find. Ticker symbols are limited to 4 characters for the NYSE and NASDAQ.",
    "On May 6, 2010, the U.S. stock market experienced a “flash crash,” where the Dow Jones plunged nearly 1,000 points in just minutes, wiping out about $1 trillion in market value before quickly rebounding.",
    "A major financial crisis in 1907 led to the creation of the Federal Reserve. During the crisis, stock prices fell almost 50%, leading to widespread panic and bank failures.",
    "The Charging Bull statue near Wall Street in New York City was installed in 1989 as a guerrilla art project by sculptor Arturo Di Modica. The bull was meant to symbolize the strength and resilience of the American people, but it became so popular that the city allowed it to stay.",
    "Rubbing the Charging Bull's horns or nose is believed by some tourists to bring good luck in trading. Many visitors make a point of rubbing it for a little extra financial luck!",
    "In 2010, a programmer named Laszlo Hanyecz made the first real-world Bitcoin transaction by buying two pizzas for 10,000 Bitcoins. Today, that pizza would be worth hundreds of millions of dollars.",
    "The New York Stock Exchange takes a lunch break…kind of. The market doesn’t officially close for lunch, but activity slows down considerably between 11:30 AM and 1:30 PM, with many traders hitting nearby delis or cafes for a quick bite.",
    "There's a superstition that the stock market performs worse on Fridays that fall on the 13th. While there’s no real evidence to support this, many investors still approach these Fridays with caution.",
    "The terms \"bull market\" (rising prices) and \"bear market\" (falling prices) come from the way these animals attack their prey. Bulls thrust their horns upward, while bears swipe their paws downward.",
    "Wall Street is famous for its \"ticker tape parades,\" but did you know the first one wasn't even planned? It started spontaneously in 1886 when New Yorkers threw ticker tape out the windows to celebrate the Statue of Liberty’s dedication.",
    "\"FOMO\" (Fear of Missing Out) is a real phenomenon in the stock market! Investors often jump into stocks they see rising quickly, fearing they'll miss a big opportunity, even though this behavior can be risky.",
    "Some companies choose stock ticker symbols that match their brand or add a fun twist. For example, the stock ticker for Dunkin' Donuts used to be \"DNKN,\" while the software company Citrix used the symbol \"CTXS.\"",
    "On Wall Street, low-quality, speculative stocks are often referred to as “cats and dogs.” They tend to be more volatile and risky, but some traders love the thrill of investing in them.",
    "Companies like Apple and Tesla have done multiple stock splits to make their shares more affordable for everyday investors. Tesla once did a 5-for-1 split, turning each share into five smaller shares, making it easier for more people to buy in.",
    "CNN has a \"Fear and Greed Index\" that tracks the emotions of investors. It ranges from \"Extreme Fear\" to \"Extreme Greed,\" reflecting the current mood of the market.",
    "In 1999, a magazine had a dog named \"Stella\" randomly select stocks by tossing her toy on a grid of stock options. She beat most professional fund managers in that year’s stock performance!",
    "In 1929, Goodyear blimps were first flown over Wall Street to advertise stocks in a unique way, literally taking stock market advertising to new heights!",
    "In 2015, a professional eSports team named \"Fnatic\" went public in a strange twist, making it possible to invest in a gaming team on the stock exchange.",
    "Microsoft was approached by Google in 1999 to buy the company for $1 million. Microsoft said no. Fast forward a few decades, and Google is now worth over $1.5 trillion!",
    "In 2021, YouTuber Michael Reeves created a project where he used a fish to randomly trade stocks. The fish, named \"Frederick,\" swam around a fish tank divided into different stock options, and wherever the fish swam, it would make a trade. Frederick’s random stock picks even outperformed some human traders!",
    "In 2013, the Wall Street Journal hosted a contest between professional traders and a cat named Orlando. Orlando picked stocks by tossing a toy mouse on a grid of companies, and, to everyone’s surprise, the cat outperformed the pros by the end of the year!",
    "Some traders joke about using a \"Magic 8-Ball\" to make stock decisions. It might say things like \"Buy now!\" or \"Ask again later!\"—which could still be as accurate as some human predictions!",
    "In 2018, Elon Musk famously tweeted that he was considering taking Tesla private at $420 a share, causing the stock to skyrocket and the market to go into a frenzy. That one tweet ended up costing him and Tesla $20 million in SEC fines!",
    "In the 1990s, a chicken named \"Kentucky\" was trained to pick stocks by pecking at grains of corn placed on different stock options. Kentucky's picks outperformed many top financial analysts, proving that luck can sometimes be better than expertise!",
    "In early 2021, GameStop's stock became the battleground between Reddit day traders and hedge funds, leading to a wild rollercoaster of trading. What started as a meme stock exploded into a global frenzy, with people making (and losing) millions.",
    "In 2014, a man raised over $55,000 on Kickstarter to make a single bowl of potato salad. It wasn’t a stock investment, but it shows how quirky the world of crowdfunding and investing can be!",
    "Dogecoin, the cryptocurrency that started as a joke, surged to over $80 billion in market value in 2021, fueled by internet memes and tweets from Elon Musk. It became a lesson in how unpredictable (and funny) the market can be!",
    "In 2012, Apple’s stock price briefly dipped because of a typo in an analyst’s report. The analyst meant to write \"iPod,\" but they accidentally wrote \"iPoo,\" causing a lot of laughter—and a temporary dip in stock prices.",
    "In 2020, a fake rumor spread online that the beloved burger chain In-N-Out was going public. Despite it being a prank, people got excited, and some even tried to figure out how to invest—before realizing it was all a hoax.",
    "Good things take time. Sit back, grab a cup of coffee, and relax!",
    "One of the lyrics in Radiohead's 2003 song \"A Wolf at the Door\" says \"investments and dealers.\" This is a subtle reference to the volatility of the stock market! A fitting addition to an album titled \"Hail to the Thief\"!",


    "You have just lost the game.",
    "On an alarming number of occasions, animals have outperformed human investors with blind luck. Informed investing is the real key to success in the stock market. Avoid any monkey business!",
    "Flipping a coin.... Heads!",
    "Flipping a coin.... Tails!",
    "Screaming helps relax your throat muscles by 32.5%. If you've had a rough day, take that 32.5% and run with it!",
    "Other than this, exactly one of the facts here are made up. Stay careful, and remember-don't trust anyone!",
    "Have you tried simply waiting faster?",
    "Tired of waiting? Get up, look into the mirror and thrice chant \"Elon Musk\". If you're lucky, he might give you a doge coin! If not... Well, at least with no crumple zones it will be quick.",
    "Your Wii is not thirsty, it does not want orange juice.",
    "This may take some time... Our top analysts are busy arguing over who gets the red crayon.",
    "Have you seen the green crayons? I'm worried our analysts might have gotten hungry again...",
  ]

  useEffect(() => {
    const factoidElement = document.getElementById(`factoid-text-${factoidCount - 1}`);
    if (factoidElement) {
      factoidElement.addEventListener('animationend', handleAnimationEnd);
    }

    return () => {
      if (factoidElement) {
        factoidElement.removeEventListener('animationend', handleAnimationEnd);
      }
    };
  }, [factoidCount]);

  const handleAnimationEnd = (e) => {
    if (e.animationName === 'cycle-factoids') {
      createNewFactoid();
      //removeOldFactoids(); // Remove factoids no longer shown
    }
  };

  const createNewFactoid = () => {
    // Select a random factoid from the list
    const newFactoid = factoidList[Math.floor(Math.random() * factoidList.length)];
    
    setFactoidCount(factoidCount + 1);
    setFactoids((prevFactoids) => [...prevFactoids, newFactoid]);
  };

  const removeOldFactoids = () => {
    // Remove factoids that are too old (only keep the last 3 factoids)
    setFactoids((prevFactoids) => {
      if (prevFactoids.length > 3) {
        return prevFactoids.slice(-3); // Keep only the last 3 factoids
      }
      return prevFactoids;
    });
  };

  return (
    <div id="load-screen-animation-container">
      {factoids.map((factoid, index) => (
        <div
          id={`factoid-text-${index}`}
          key={index}
          className="factoid-text"
          style={{ animationDelay: 0 }} // Stagger the animation for each new factoid
        >
          {factoid}
        </div>
      ))}
      <div id="salmon-square">load</div>
      <div id="green-square">ing</div>
      <div id="background-square"></div>
    </div>
  );
}

function GraphicalData({
  error,
  stockData,
  chartData,
  rangeValue,
  setRangeValue,
  rangeUnit,
  setRangeUnit,
}) {

  return (
    
    <>
      {error && <p style={{ color: 'red' }}>{error}</p>}

      {stockData && (
        <div style={{color: 'black'}}>
          {(() => {
            console.log(rangeUnit);
            console.log(rangeValue);
            return null; // Return null to avoid rendering issues
          })()}
          <h2>
            {stockData.longName} ({stockData.symbol})
          </h2>
          <p>Price: {stockData.regularMarketPrice}</p>
          <p>Open: {stockData.regularMarketOpen}</p>
          <p>High: {stockData.regularMarketDayHigh}</p>
          <p>Low: {stockData.regularMarketDayLow}</p>
        </div>
      )}

      {chartData && (
        <div style={{ width: '80%', height: '400px' }}>
          <Line data={chartData} options={{ maintainAspectRatio: false }} />
        </div>
      )}


    </>
  );
}


function App() {
  const [ticker, setTicker] = useState('');
  const [stockData, setStockData] = useState(null);
  const [chartData, setChartData] = useState(null);
  const [rangeValue, setRangeValue] = useState(7);
  const [rangeUnit, setRangeUnit] = useState('days');
  const [error, setError] = useState(null);
  const [showAnimation, setShowAnimation] = useState(false); // State for showing animation
  const [showStockInfo, setShowStockInfo] = useState(false); // State for showing stock info
  const [showGraph, setShowGraph] = useState(false); // State for showing stock info

  const handleSearch = async () => {
    setError(null); // Reset error state before making new requests
    setStockData(null); // Clear previous stock data
    setChartData(null); // Clear previous chart data
    setShowAnimation(true); // Show the loading animation
    setShowStockInfo(false); // Hide stock info until data is ready
    // Hide certain UI elements
    const search = document.getElementById("search-header-component");
    const range = document.getElementById("range-header-component");
    const title = document.getElementById("title");

    search.classList.add("hide");
    range.classList.add("hide");
    title.classList.add("hide");
    

    // Simulate a 5-second delay for the loading screen, regardless of fetching status
    setTimeout(() => {
      setShowAnimation(false); // Hide the loading animation after 5 seconds
      setShowGraph(true);
    }, 5000); // 5 seconds delay for testing purposes

    if (ticker) {
      try {
        // Fetch stock data (replace with your API call)
        //about to make the functino call
        const stockInfo = await fetchStockData(ticker);
        setStockData(stockInfo);
  
        // Fetch historical data (replace with your API call)
        const { labels, prices } = await fetchHistoricalData(ticker, rangeValue, rangeUnit);
  
        const data = {
          labels: labels,
          datasets: [
            {
              label: 'Stock Price',
              data: prices,
              fill: false,
              borderColor: 'rgb(75, 192, 192)',
              tension: 0.1,
            },
          ],
        };
  
        setChartData(data);
  
        // After successful data fetch, show stock info and chart
        setShowStockInfo(true);  // <---- Add this line to show stock info
  
      } catch (error) {
        setError(error.message);
      }
    } else{
      console.log("Ticker is null!");
    }
  };

  return (
    <div className="App">
      <h1 className="header-title" id="title">Stock Data App</h1>

      <div id="search-header-component">
        <input
          type="text"
          id="ticker"
          name="ticker"
          placeholder="Enter stock ticker"
          value={ticker}
          onChange={(e) => setTicker(e.target.value)}
        />
        <button onClick={handleSearch}>Search</button>
      </div>

      {showAnimation && <LoadScreen />} {/* Show the loading screen */}
      {showGraph && 
      <GraphicalData
      error={error}
      stockData={stockData}
      chartData={chartData} // Pass chartData to show the graph
      rangeValue={rangeValue}
      setRangeValue={setRangeValue}
      rangeUnit={rangeUnit}
      setRangeUnit={setRangeUnit} />}

      {/* Range component (assumed to be somewhere else in the app) */}
      <div id="range-header-component">
        <label id="range">
          Range:
          <input
            type="number"
            value={rangeValue}
            onChange={(e) => setRangeValue(Number(e.target.value))}
            min="1"
          />
        </label>
        <label>
          Unit:
          <select value={rangeUnit} onChange={(e) => setRangeUnit(e.target.value)}>
            <option value="days">Days</option>
            <option value="months">Months</option>
            <option value="years">Years</option>
          </select>
        </label>
      </div>
    </div>
  );
}

export default App;