# 2lazy2build

A real-time PC deal aggregator that scrapes and filters the best prebuilt desktop and laptop deals from popular retailers.

![2lazy2build Screenshot](screenshot.png)

## Features

- **Real-time Scraping**: Fetches current deals from:
  - Newegg
  - eBay
  - More retailers coming soon (Amazon, Best Buy, Micro Center)

- **Advanced Filtering**:
  - CPU selection (Intel i5/i7/i9, AMD Ryzen 5/7/9)
  - GPU selection (RTX 40/50 series, RX 7000/9000 series)
  - Price range
  - Minimum RAM
  - Minimum Storage
  - Device type (Desktop/Laptop)
  - Brand preferences
  - In-stock status
  - Refurbished condition

- **User Interface**:
  - Grid and List view options
  - Real-time price sorting
  - Clean, modern design with a purple theme
  - Responsive layout for all devices
  - Loading states and error handling

## Tech Stack

### Frontend
- Next.js 15.3.2
- React 19
- TypeScript
- Tailwind CSS
- Headless UI Components

### Backend
- Python FastAPI
- Web scraping utilities
- Real-time data processing

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.8+
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/2lazy2build.git
cd 2lazy2build
```

2. Install frontend dependencies:
```bash
cd frontend
npm install
```

3. Install backend dependencies:
```bash
cd backend
pip install -r requirements.txt
```

### Running the Application

1. Start the backend server:
```bash
cd backend
python main.py
```

2. Start the frontend development server:
```bash
cd frontend
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

## Usage

1. Select your desired filters from the left sidebar:
   - Choose CPU and GPU preferences
   - Set price range and minimum specs
   - Select device type (Desktop/Laptop)
   - Choose preferred retailers

2. Click "Search Deals" to fetch real-time results

3. Use the view toggle to switch between grid and list views

4. Sort results by price using the sort controls

5. Click "View on [Retailer]" to visit the original listing

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to all the retailers whose products are featured
- Built with modern web technologies and best practices
- Inspired by the PC building community

## Contact

Your Name - [@yourtwitter](https://twitter.com/yourtwitter)

Project Link: [https://github.com/yourusername/2lazy2build](https://github.com/yourusername/2lazy2build)

## Roadmap

- [ ] Add support for Amazon
- [ ] Add support for Best Buy
- [ ] Add support for Micro Center
- [ ] Add price history tracking
- [ ] Add email notifications for price drops
- [ ] Add user accounts for saved searches
- [ ] Add comparison feature 
