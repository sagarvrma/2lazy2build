'use client'

import { useState, Fragment } from 'react'
import Image from 'next/image'
import { Listbox, Transition } from '@headlessui/react'
import { CheckIcon, ChevronsUpDownIcon, FilterIcon, XIcon } from 'lucide-react'

interface PC {
  id: string
  title: string
  price: number
  image: string
  cpu: string
  gpu: string
  ram: string
  storage: string
  refurbished: boolean
  inStock: boolean
  source: 'Newegg' | 'eBay' | 'Best Buy'
  url: string
  brand: string
  device_type: 'desktop' | 'laptop' | 'unknown'
}

const cpuOptions = ['Intel i5', 'Intel i7', 'Intel i9', 'AMD Ryzen 5', 'AMD Ryzen 7', 'AMD Ryzen 9']
const gpuOptions = [
  'RTX 5090', 'RTX 5080', 'RTX 5070 Ti', 'RTX 5070', 'RTX 5060 Ti', 'RTX 5060',
  'RTX 4090', 'RTX 4080 Super', 'RTX 4080', 'RTX 4070 Ti Super', 'RTX 4070 Super',
  'RTX 4070', 'RTX 4060 Ti', 'RTX 4060', 'RTX 3090', 'RTX 3080', 'RTX 3070',
  'RX 9070 XT', 'RX 7900 XTX', 'RX 7800 XT'
]
const brandOptions = ['All', 'hp', 'msi', 'dell', 'asus', 'acer', 'cyberpowerpc', 'ibuypower', 'generic']
const sortOptions = ['Relevance', 'Price: Low to High', 'Price: High to Low']
const deviceTypeOptions = ['Both', 'Desktop', 'Laptop']
const sourceOptions = ['All', 'Newegg', 'eBay', 'Best Buy']

function MultiSelect({ label, options, selected, setSelected }: {
  label: string
  options: string[]
  selected: string[]
  setSelected: (val: string[]) => void
}) {
  const toggle = (value: string) => {
    setSelected(selected.includes(value)
      ? selected.filter((v) => v !== value)
      : [...selected, value])
  }

  return (
    <div className="mb-6">
      <h3 className="font-semibold text-white mb-2">{label}</h3>
      <div className="bg-purple-800/50 border border-purple-600 rounded p-2 max-h-48 overflow-y-auto">
        {options.map((opt) => (
          <label key={opt} className="flex items-center space-x-2 py-1">
            <input
              type="checkbox"
              checked={selected.includes(opt)}
              onChange={() => toggle(opt)}
              className="text-purple-500 focus:ring-purple-500"
            />
            <span className="text-gray-300">{opt}</span>
          </label>
        ))}
      </div>
    </div>
  )
}

export default function Home() {
  const [selectedCPUs, setSelectedCPUs] = useState<string[]>([])
  const [selectedGPUs, setSelectedGPUs] = useState<string[]>([])
  const [selectedBrands, setSelectedBrands] = useState<string[]>([])
  const [sortOrder, setSortOrder] = useState(sortOptions[0])
  const [maxPrice, setMaxPrice] = useState('')
  const [minRAM, setMinRAM] = useState('')
  const [minStorage, setMinStorage] = useState('')
  const [inStockOnly, setInStockOnly] = useState(false)
  const [refurbishedOnly, setRefurbishedOnly] = useState(false)
  const [deviceType, setDeviceType] = useState<string>('Both')
  const [selectedSource, setSelectedSource] = useState<string>('All')
  const [results, setResults] = useState<PC[]>([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const [showReminder, setShowReminder] = useState(true)
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [currentSort, setCurrentSort] = useState<'asc' | 'desc' | null>(null)

  const handleFilterChange = async () => {
    setLoading(true)
    setSearched(true)
    
    const params = new URLSearchParams()
    if (selectedCPUs.length) params.set('cpu', selectedCPUs.join(','))
    if (selectedGPUs.length) params.set('gpu', selectedGPUs.join(','))
    if (maxPrice) params.set('max_price', maxPrice)
    if (minRAM) params.set('min_ram', minRAM)
    if (minStorage) params.set('min_storage', minStorage)
    if (inStockOnly) params.set('in_stock', 'true')
    if (refurbishedOnly) params.set('refurbished', 'true')
    if (deviceType !== 'Both') params.set('device_type', deviceType.toLowerCase())
    if (selectedSource !== 'All') params.set('source', selectedSource)

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/scrape?${params.toString()}`)
      const data = await res.json()
      let filtered = data.map((item: any, i: number) => {
        const pc: PC = {
          id: `pc-${i}`,
          title: item.title,
          price: parseFloat(item.price.replace(/[^\d.]/g, '')),
          image: item.image || '/placeholder.svg',
          cpu: item.matched_cpu,
          gpu: item.matched_gpu,
          brand: item.brand || 'Generic',
          ram: item.ram_gb ? `${item.ram_gb} GB` : 'Unknown',
          storage: item.storage_gb ? `${item.storage_gb} GB SSD` : 'Unknown',
          refurbished: item.refurbished,
          inStock: item.in_stock ?? true,
          source: item.source,
          url: item.link,
          device_type: item.device_type?.toLowerCase() || 'unknown'
        }
        return pc
      })

      if (selectedBrands.length && !selectedBrands.includes('All')) {
        filtered = filtered.filter((pc: PC) => selectedBrands.includes(pc.brand.toLowerCase()))
      }

      if (selectedSource !== 'All') {
        filtered = filtered.filter((pc: PC) => pc.source === selectedSource)
      }

      if (deviceType !== 'Both') {
        filtered = filtered.filter((pc: PC) => pc.device_type === deviceType.toLowerCase())
      }

      if (sortOrder === 'Price: Low to High') {
        filtered.sort((a: PC, b: PC) => a.price - b.price)
      } else if (sortOrder === 'Price: High to Low') {
        filtered.sort((a: PC, b: PC) => b.price - a.price)
      }

      setResults(filtered)
    } catch (err) {
      console.error('Error fetching data:', err)
    } finally {
      setLoading(false)
    }
  }

  const toggleCPU = (cpu: string) => {
    setSelectedCPUs(prev => 
      prev.includes(cpu) ? prev.filter(c => c !== cpu) : [...prev, cpu]
    )
  }

  const toggleGPU = (gpu: string) => {
    setSelectedGPUs(prev => 
      prev.includes(gpu) ? prev.filter(g => g !== gpu) : [...prev, gpu]
    )
  }

  const sortResults = (direction: 'asc' | 'desc') => {
    setCurrentSort(direction)
    setResults(prev => [...prev].sort((a, b) => 
      direction === 'asc' ? a.price - b.price : b.price - a.price
    ))
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-800 to-purple-900">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-10 relative">
          <div className="absolute inset-0 -z-10 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-purple-600 to-transparent opacity-20 blur-3xl"></div>
          <h1 className="text-6xl font-extrabold tracking-tight text-purple-300 mb-2">
            2lazy2build
          </h1>
          <div className="flex flex-col items-center">
            <p className="text-lg text-gray-300 mb-1">Scraped from Newegg and eBay in real-time</p>
            <span className="px-4 py-1.5 bg-purple-800/50 rounded-full text-sm text-gray-300 border border-purple-500/30">
              Amazon, Best Buy, Micro Center and more coming soon!
            </span>
          </div>
        </header>

        {showReminder && (
          <div className="bg-purple-800/30 backdrop-blur-sm rounded-xl shadow-lg border border-purple-500/30 p-4 mb-6 relative">
            <div className="flex items-center justify-between">
              <div className="flex items-start space-x-3">
                <div className="bg-purple-700/20 p-2 rounded-lg">
                  <svg className="h-6 w-6 text-purple-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
                  </svg>
                </div>
                <div>
                  <h3 className="font-bold text-white text-lg">Don't forget to bookmark your favorite deals!</h3>
                  <p className="text-gray-300">
                    Use your browser's bookmark feature to save listings you're interested in for later.
                  </p>
                </div>
              </div>
              <button 
                className="text-gray-400 hover:text-white"
                onClick={() => setShowReminder(false)}
              >
                <XIcon className="h-5 w-5" />
                <span className="sr-only">Dismiss</span>
              </button>
            </div>
          </div>
        )}

        <div className="flex flex-col lg:flex-row gap-6">
          <div className="lg:w-1/4 lg:sticky lg:top-4 lg:self-start">
            <div className="bg-purple-900/70 backdrop-blur-sm rounded-xl shadow-lg border border-purple-700/50 p-6">
              <div className="flex items-center mb-6">
                <FilterIcon className="mr-2 h-5 w-5 text-purple-400" />
                <h2 className="text-xl font-bold text-white">Filters</h2>
              </div>

              <div className="space-y-6">
                <div className="mb-6">
                  <h3 className="font-semibold text-white mb-2">Device Type</h3>
                  <div className="space-y-2">
                    {['Both', 'Desktop', 'Laptop'].map((type) => (
                      <label key={type} className="flex items-center space-x-2">
                        <input
                          type="radio"
                          name="deviceType"
                          value={type}
                          checked={deviceType === type}
                          onChange={(e) => setDeviceType(e.target.value)}
                          className="text-purple-500 focus:ring-purple-500"
                        />
                        <span className="text-gray-300">{type}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <MultiSelect 
                  label="CPUs" 
                  options={cpuOptions} 
                  selected={selectedCPUs} 
                  setSelected={setSelectedCPUs} 
                />
                
                <MultiSelect 
                  label="GPUs" 
                  options={gpuOptions} 
                  selected={selectedGPUs} 
                  setSelected={setSelectedGPUs} 
                />

                <MultiSelect 
                  label="Brands" 
                  options={brandOptions} 
                  selected={selectedBrands} 
                  setSelected={setSelectedBrands} 
                />

                <div className="mb-6">
                  <h3 className="font-semibold text-white mb-2">Source</h3>
                  <div className="space-y-2">
                    {['All', 'Newegg', 'eBay'].map((source) => (
                      <label key={source} className="flex items-center space-x-2">
                        <input
                          type="radio"
                          name="source"
                          value={source}
                          checked={selectedSource === source}
                          onChange={(e) => setSelectedSource(e.target.value)}
                          className="text-purple-500 focus:ring-purple-500"
                        />
                        <span className="text-gray-300">{source}</span>
                      </label>
                    ))}
                  </div>
                  <div className="mt-2">
                    <span className="inline-block px-3 py-1 bg-purple-700/30 rounded-full text-xs text-purple-300">
                      More retailers coming soon!
                    </span>
                  </div>
                </div>

                <div className="mb-6">
                  <h3 className="font-semibold text-white mb-2">Sort By</h3>
                  <select
                    value={sortOrder}
                    onChange={(e) => setSortOrder(e.target.value)}
                    className="w-full bg-purple-800/50 border border-purple-600 rounded px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    {sortOptions.map((opt) => (
                      <option key={opt} value={opt}>{opt}</option>
                    ))}
                  </select>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block font-semibold text-white mb-2">Max Price ($)</label>
                    <input
                      type="number"
                      value={maxPrice}
                      onChange={(e) => setMaxPrice(e.target.value)}
                      className="w-full bg-purple-800/50 border border-purple-600 rounded px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                      placeholder="Enter maximum price"
                    />
                  </div>

                  <div>
                    <label className="block font-semibold text-white mb-2">Min RAM (GB)</label>
                    <input
                      type="number"
                      value={minRAM}
                      onChange={(e) => setMinRAM(e.target.value)}
                      className="w-full bg-purple-800/50 border border-purple-600 rounded px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                      placeholder="Enter minimum RAM"
                    />
                  </div>

                  <div>
                    <label className="block font-semibold text-white mb-2">Min Storage (GB)</label>
                    <input
                      type="number"
                      value={minStorage}
                      onChange={(e) => setMinStorage(e.target.value)}
                      className="w-full bg-purple-800/50 border border-purple-600 rounded px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                      placeholder="Enter minimum storage"
                    />
                  </div>

                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={inStockOnly}
                      onChange={(e) => setInStockOnly(e.target.checked)}
                      className="text-purple-500 focus:ring-purple-500"
                    />
                    <label className="text-white">In Stock Only</label>
                  </div>

                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={refurbishedOnly}
                      onChange={(e) => setRefurbishedOnly(e.target.checked)}
                      className="text-purple-500 focus:ring-purple-500"
                    />
                    <label className="text-white">Show Refurbished</label>
                  </div>
                </div>

                <button 
                  onClick={handleFilterChange} 
                  disabled={loading} 
                  className="w-full bg-purple-600 text-white py-2 rounded hover:bg-purple-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Searching...' : 'Search Deals'}
                </button>
              </div>
            </div>
          </div>

          <div className="lg:w-3/4">
            {loading ? (
              <div className="bg-purple-900/70 backdrop-blur-sm rounded-xl shadow-lg border border-purple-700/50 p-12 text-center">
                <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-purple-300 mx-auto mb-4"></div>
                <p className="text-purple-300 text-lg">Searching for the best deals...</p>
              </div>
            ) : !searched ? (
              <div className="bg-purple-900/70 backdrop-blur-sm rounded-xl shadow-lg border border-purple-700/50 p-12 text-center">
                <div className="mx-auto w-24 h-24 mb-6 text-purple-400">
                  <svg className="w-full h-full" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="11" cy="11" r="8" />
                    <path d="M21 21l-4.35-4.35" />
                  </svg>
                </div>
                <h2 className="text-3xl font-bold text-white mb-4">Find Your Perfect PC</h2>
                <p className="text-gray-300 mb-8">
                  Use the filters on the left to search for the best deals on
                  prebuilt PCs from Newegg and eBay.
                </p>
                <button
                  onClick={handleFilterChange}
                  className="inline-flex items-center px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-lg transition-colors duration-200"
                >
                  <svg className="w-5 h-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
                  </svg>
                  Search All Deals
                </button>
              </div>
            ) : results.length === 0 ? (
              <div className="bg-purple-900/70 backdrop-blur-sm rounded-xl shadow-lg border border-purple-700/50 p-12 text-center">
                <div className="mx-auto w-24 h-24 mb-6 text-purple-400">
                  <svg className="w-full h-full" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h2 className="text-3xl font-bold text-white mb-4">No Results Found</h2>
                <p className="text-gray-300">
                  Try adjusting your filters to find more PCs.
                </p>
              </div>
            ) : (
              <div>
                <div className="mb-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                  <div className="flex space-x-2">
                    <button
                      onClick={() => setViewMode('grid')}
                      className={`px-4 py-2 rounded ${
                        viewMode === 'grid' 
                          ? 'bg-purple-600 text-white' 
                          : 'bg-purple-800/50 text-gray-300'
                      }`}
                    >
                      Grid View
                    </button>
                    <button
                      onClick={() => setViewMode('list')}
                      className={`px-4 py-2 rounded ${
                        viewMode === 'list' 
                          ? 'bg-purple-600 text-white' 
                          : 'bg-purple-800/50 text-gray-300'
                      }`}
                    >
                      List View
                    </button>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <span className="text-gray-300">Sort by price:</span>
                    <button
                      onClick={() => sortResults('asc')}
                      className={`px-4 py-2 rounded ${
                        currentSort === 'asc'
                          ? 'bg-purple-600 text-white'
                          : 'bg-purple-800/50 text-gray-300'
                      }`}
                    >
                      Lowest First
                    </button>
                    <button
                      onClick={() => sortResults('desc')}
                      className={`px-4 py-2 rounded ${
                        currentSort === 'desc'
                          ? 'bg-purple-600 text-white'
                          : 'bg-purple-800/50 text-gray-300'
                      }`}
                    >
                      Highest First
                    </button>
                  </div>
                </div>

                <div className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4' : 'space-y-4'}>
                  {results.map((pc) => (
                    <div
                      key={pc.id}
                      className={`bg-purple-900/70 backdrop-blur-sm rounded-xl shadow-lg border border-purple-700/50 overflow-hidden ${
                        viewMode === 'list' ? 'flex' : ''
                      }`}
                    >
                      <div className={`relative ${viewMode === 'list' ? 'w-48 h-48 flex-shrink-0' : 'aspect-square'}`}>
                        <Image
                          src={pc.image}
                          alt={pc.title}
                          fill
                          className="object-contain p-4"
                        />
                        <div className="absolute top-2 right-2">
                          <span className="px-2 py-1 rounded text-xs bg-purple-500/20 text-purple-300">
                            {pc.source}
                          </span>
                        </div>
                        <div className="absolute top-2 left-2">
                          <span className="px-2 py-1 rounded text-xs bg-purple-500/20 text-purple-300">
                            {pc.device_type === 'desktop' ? 'Desktop' : 'Laptop'}
                          </span>
                        </div>
                      </div>

                      <div className={`${viewMode === 'list' ? 'flex-1' : ''} p-4`}>
                        <div className="flex items-start justify-between gap-4 mb-3">
                          <div>
                            <h3 className="text-white font-semibold line-clamp-2">{pc.title}</h3>
                          </div>
                          <span className="text-xl font-bold text-purple-300 whitespace-nowrap">
                            ${pc.price.toLocaleString()}
                          </span>
                        </div>

                        <div className="grid grid-cols-2 gap-3 mb-4 text-sm">
                          <div>
                            <p className="text-gray-400">CPU</p>
                            <p className="text-gray-300">{pc.cpu}</p>
                          </div>
                          <div>
                            <p className="text-gray-400">GPU</p>
                            <p className="text-gray-300">{pc.gpu}</p>
                          </div>
                          <div>
                            <p className="text-gray-400">RAM</p>
                            <p className="text-gray-300">{pc.ram}</p>
                          </div>
                          <div>
                            <p className="text-gray-400">Storage</p>
                            <p className="text-gray-300">{pc.storage}</p>
                          </div>
                        </div>

                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <span className={`px-2 py-1 rounded-full text-xs ${
                              pc.inStock ? 'bg-green-500/20 text-green-300' : 'bg-red-500/20 text-red-300'
                            }`}>
                              {pc.inStock ? '✓ In Stock' : '× Out of Stock'}
                            </span>
                            {pc.refurbished && (
                              <span className="px-2 py-1 rounded-full text-xs bg-yellow-500/20 text-yellow-300">
                                Refurbished
                              </span>
                            )}
                          </div>
                        </div>

                        <a
                          href={pc.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="mt-4 block w-full text-center px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded transition-colors duration-200"
                        >
                          View on {pc.source}
                        </a>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
