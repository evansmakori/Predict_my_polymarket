# 🔗 Test URLs for Market Extraction

Use these Polymarket URLs to test the dashboard's extraction feature.

## Popular Events

### Politics

```
https://polymarket.com/event/presidential-election-winner-2024
https://polymarket.com/event/who-will-win-the-2024-presidential-election
https://polymarket.com/event/will-donald-trump-be-president-on-june-1-2025
```

### Crypto

```
https://polymarket.com/event/bitcoin-price-on-december-31-2024
https://polymarket.com/event/will-ethereum-etf-be-approved-in-2024
```

### Sports

```
https://polymarket.com/event/super-bowl-winner-2025
https://polymarket.com/event/nba-champion-2024-25
```

### Tech

```
https://polymarket.com/event/will-sam-altman-be-openai-ceo-on-december-31-2024
https://polymarket.com/event/next-apple-product-launch
```

## Individual Markets

If you prefer to extract specific markets rather than entire events:

```
https://polymarket.com/market/will-biden-be-the-2024-democratic-nominee
https://polymarket.com/market/will-trump-be-convicted-in-2024
```

## How to Use

1. Copy any URL above
2. Go to **Extract Market** page in the dashboard
3. Paste the URL
4. Click **"Extract Data"**
5. Wait ~30 seconds for the extraction to complete
6. View your market in the dashboard!

## Tips

- **Events** contain multiple markets (e.g., an election event might have markets for each candidate)
- **Markets** are individual prediction questions
- The extractor works with both types of URLs
- Popular events may take longer to extract due to multiple markets

## Troubleshooting

**"URL not found" error?**
- The event/market may have been closed or removed
- Try a different URL from the list above

**Extraction taking too long?**
- Events with many markets (10+) can take 1-2 minutes
- Be patient, the backend is fetching orderbook data and price history for each market

**No data showing?**
- Check that the backend is running (http://localhost:8000/health)
- Look for errors in the browser console
- Check backend logs in the terminal

## Finding New URLs

Visit [Polymarket.com](https://polymarket.com) to find more markets:

1. Browse categories (Politics, Crypto, Sports, etc.)
2. Click on any event or market
3. Copy the URL from your browser
4. Use it in the dashboard!

---

**Pro Tip**: Start with smaller events (1-3 markets) to test quickly, then move to larger events once everything is working!
