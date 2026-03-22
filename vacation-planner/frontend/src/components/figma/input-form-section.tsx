import { motion, AnimatePresence } from "motion/react";
import { useState, useEffect, useMemo } from "react";
import Image from "next/image";
import { useDebounce } from "@/hooks/useDebounce";
import { 
  Wallet, 
  Heart, 
  Zap, 
  Moon, 
  PartyPopper, 
  Eye, 
  UtensilsCrossed,
  MapPin,
  Users,
  ArrowRight,
  Plane,
  CalendarDays,
  AlertTriangle,
} from "lucide-react";

interface FormData {
  budget: string;
  lifestyle: string;
  vacationType: string;
  origin: string;
  destination: string;
  startDate: string;
  endDate: string;
  travelers: string;
}

export function InputFormSection({ onSubmit }: { onSubmit: (data: FormData) => void }) {
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState<FormData>({
    budget: "",
    lifestyle: "",
    vacationType: "",
    origin: "",
    destination: "",
    startDate: "",
    endDate: "",
    travelers: "",
  });

  // --- Nominatim Autocomplete State (shared for Origin + Destination) ---
  const [originInput, setOriginInput] = useState("");
  const [originSuggestions, setOriginSuggestions] = useState<{ place_id: number; display_name: string }[]>([]);
  const [originLoading, setOriginLoading] = useState(false);
  const [selectedOrigin, setSelectedOrigin] = useState("");
  const [originHighlight, setOriginHighlight] = useState(-1);

  const [destInput, setDestInput] = useState("");
  const [destSuggestions, setDestSuggestions] = useState<{ place_id: number; display_name: string }[]>([]);
  const [destLoading, setDestLoading] = useState(false);
  const [selectedDest, setSelectedDest] = useState("");
  const [destHighlight, setDestHighlight] = useState(-1);

  const debouncedOrigin = useDebounce(originInput, 500);
  const debouncedDest = useDebounce(destInput, 500);

  // --- Nominatim Fetch (reusable) ---
  const fetchNominatim = async (
    term: string,
    selected: string,
    setSuggestions: (s: { place_id: number; display_name: string }[]) => void,
    setLoading: (b: boolean) => void,
    setHighlight: (n: number) => void,
  ) => {
    if (term && term !== selected) {
      setLoading(true);
      try {
        const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(term)}&featuretype=city,settlement&limit=5`;
        const response = await fetch(url, {
          headers: {
            'Accept-Language': 'en-US,en;q=0.9',
            'User-Agent': 'VacationPlannerApp/1.0'
          }
        });
        if (!response.ok) throw new Error('Geocoding failed');
        const data = await response.json();
        const parsed = data.map((item: any) => {
          const parts = item.display_name.split(',').map((p: string) => p.trim());
          const formatted = parts.length >= 3 
            ? `${parts[0]}, ${parts[parts.length - 1]}`
            : item.display_name;
          return { place_id: item.place_id, display_name: formatted };
        });
        setSuggestions(parsed);
        setHighlight(-1);
      } catch (error) {
        console.error("Geocoding error", error);
      } finally {
        setLoading(false);
      }
    } else {
      setSuggestions([]);
      setHighlight(-1);
    }
  };

  useEffect(() => {
    fetchNominatim(debouncedOrigin, selectedOrigin, setOriginSuggestions, setOriginLoading, setOriginHighlight);
  }, [debouncedOrigin, selectedOrigin]);

  useEffect(() => {
    fetchNominatim(debouncedDest, selectedDest, setDestSuggestions, setDestLoading, setDestHighlight);
  }, [debouncedDest, selectedDest]);


  // --- Date Validation ---
  const today = useMemo(() => {
    const d = new Date();
    return d.toISOString().split("T")[0];
  }, []);

  const tripDays = useMemo(() => {
    if (!formData.startDate || !formData.endDate) return 0;
    const start = new Date(formData.startDate);
    const end = new Date(formData.endDate);
    const diff = Math.round((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));
    return diff;
  }, [formData.startDate, formData.endDate]);

  const dateError = useMemo(() => {
    if (!formData.startDate || !formData.endDate) return null;
    if (tripDays <= 0) return "Check-out must be after check-in.";
    if (tripDays > 5) return "Trips are currently limited to a maximum of 5 days.";
    return null;
  }, [formData.startDate, formData.endDate, tripDays]);

  const datesValid = formData.startDate && formData.endDate && !dateError && tripDays > 0;


  const steps = [
    { id: "budget", title: "Budget Tier" },
    { id: "lifestyle", title: "Your Lifestyle" },
    { id: "vacationType", title: "Vacation Type" },
    { id: "origin", title: "Where are you flying from?" },
    { id: "destination", title: "Where are you going?" },
    { id: "dates", title: "Travel Dates" },
    { id: "travelers", title: "Travelers" },
  ];

  const budgetOptions = [
    { id: "low", label: "Budget Explorer", icon: Wallet, desc: "Smart spending, big adventures", gradient: "from-emerald-500 to-teal-500" },
    { id: "medium", label: "Comfort Seeker", icon: Heart, desc: "Balance of value and comfort", gradient: "from-blue-500 to-cyan-500" },
    { id: "luxury", label: "Luxury Voyager", icon: Zap, desc: "Premium all the way", gradient: "from-purple-500 to-pink-500" },
  ];

  const lifestyleOptions = [
    { id: "relaxed", label: "Relaxed", icon: Heart, desc: "Slow-paced and serene", gradient: "from-rose-400 to-orange-400" },
    { id: "energetic", label: "Energetic", icon: Zap, desc: "Action-packed days", gradient: "from-yellow-400 to-red-500" },
    { id: "nightowl", label: "Night Owl", icon: Moon, desc: "After-dark explorer", gradient: "from-indigo-500 to-purple-600" },
  ];

  const vacationTypeOptions = [
    { id: "party", label: "Partying", icon: PartyPopper, desc: "Nightlife & celebrations", image: "https://images.unsplash.com/photo-1611464379978-2415d1678256?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxuaWdodGxpZmUlMjBjbHViJTIwcGFydHklMjBuZW9ufGVufDF8fHx8MTc3MzY3Mjg1MXww&ixlib=rb-4.1.0&q=80&w=1080" },
    { id: "sightseeing", label: "Sightseeing", icon: Eye, desc: "Culture & landmarks", image: "https://images.unsplash.com/photo-1600209892743-c50f8091b231?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxiYWxpJTIwdGVtcGxlJTIwc3Vuc2V0JTIwYXJjaGl0ZWN0dXJlfGVufDF8fHx8MTc3MzY3Mjg1MHww&ixlib=rb-4.1.0&q=80&w=1080" },
    { id: "culinary", label: "Culinary", icon: UtensilsCrossed, desc: "Food-focused journey", image: "https://images.unsplash.com/photo-1643757343278-5d50309dfa44?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxnb3VybWV0JTIwZm9vZCUyMGZpbmUlMjBkaW5pbmd8ZW58MXx8fHwxNzczNTg1MTUwfDA&ixlib=rb-4.1.0&q=80&w=1080" },
  ];

  const handleSelect = (field: keyof FormData, value: string) => {
    setFormData({ ...formData, [field]: value });
    if (currentStep < steps.length - 1) {
      setTimeout(() => setCurrentStep(currentStep + 1), 300);
    }
  };

  const handleInputChange = (field: keyof FormData, value: string) => {
    setFormData({ ...formData, [field]: value });
  };

  const handleSubmitForm = () => {
    if (formData.destination && formData.travelers && formData.origin && datesValid) {
      onSubmit(formData);
    }
  };

  // --- Reusable Nominatim Autocomplete Renderer ---
  const renderLocationStep = (config: {
    field: "origin" | "destination";
    inputValue: string;
    setInputValue: (v: string) => void;
    suggestions: { place_id: number; display_name: string }[];
    setSuggestions: (s: any[]) => void;
    isLoading: boolean;
    selectedLocation: string;
    setSelectedLocation: (v: string) => void;
    highlightedIndex: number;
    setHighlightedIndex: (n: number) => void;
    placeholder: string;
    icon: typeof MapPin;
    iconColor: string;
    focusColor: string;
    nextStep: number;
  }) => {
    const Icon = config.icon;
    return (
      <div className="max-w-2xl mx-auto">
        <div className="relative">
          <Icon className={`absolute left-6 top-1/2 -translate-y-1/2 h-6 w-6 text-[${config.iconColor}]`} />
          <input
            type="text"
            value={config.inputValue}
            onChange={(e) => {
              config.setInputValue(e.target.value);
              if (config.selectedLocation) config.setSelectedLocation("");
              handleInputChange(config.field, e.target.value);
            }}
            onKeyDown={(e) => {
              if (e.key === 'ArrowDown') {
                e.preventDefault();
                if (config.suggestions.length > 0) {
                  config.setHighlightedIndex(Math.min(config.highlightedIndex + 1, config.suggestions.length - 1));
                }
              } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                if (config.suggestions.length > 0) {
                  config.setHighlightedIndex(Math.max(config.highlightedIndex - 1, 0));
                }
              } else if (e.key === 'Enter') {
                e.preventDefault();
                if (config.suggestions.length > 0 && config.highlightedIndex >= 0) {
                  const selected = config.suggestions[config.highlightedIndex];
                  config.setInputValue(selected.display_name);
                  config.setSelectedLocation(selected.display_name);
                  handleInputChange(config.field, selected.display_name);
                  config.setSuggestions([]);
                  config.setHighlightedIndex(-1);
                } else if (formData[config.field].trim() && config.selectedLocation) {
                  setCurrentStep(config.nextStep);
                }
              }
            }}
            placeholder={config.placeholder}
            className={`w-full bg-black/5 dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-[20px] pl-16 pr-14 py-6 text-gray-900 dark:text-white text-xl placeholder:text-gray-400 dark:placeholder:text-white/40 focus:outline-none focus:border-[${config.focusColor}]/50 focus:shadow-[0_0_30px_rgba(0,240,255,0.2)] transition-all`}
            style={{ fontFamily: "'Inter', sans-serif" }}
            autoFocus
          />

          {config.isLoading && (
            <div className="absolute right-6 top-1/2 -translate-y-1/2">
              <div className="h-6 w-6 rounded-full border-2 border-[#00F0FF]/20 border-t-[#00F0FF] animate-spin" />
            </div>
          )}

          <AnimatePresence>
            {config.suggestions.length > 0 && !config.selectedLocation && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="absolute top-full left-0 right-0 mt-4 z-50 backdrop-blur-xl bg-white/80 dark:bg-[#1a1a2e]/80 border border-gray-200 dark:border-white/20 rounded-[20px] overflow-hidden shadow-[0_8px_32px_rgba(0,0,0,0.1)] dark:shadow-[0_8px_32px_rgba(0,0,0,0.5)]"
              >
                <ul className="py-2 max-h-[300px] overflow-y-auto custom-scrollbar">
                  {config.suggestions.map((suggestion, index) => (
                    <li
                      key={suggestion.place_id}
                      onMouseEnter={() => config.setHighlightedIndex(index)}
                      onClick={() => {
                        config.setInputValue(suggestion.display_name);
                        config.setSelectedLocation(suggestion.display_name);
                        handleInputChange(config.field, suggestion.display_name);
                        config.setSuggestions([]);
                        config.setHighlightedIndex(-1);
                      }}
                      className={`px-6 py-4 text-gray-800 dark:text-white/90 text-lg cursor-pointer transition-colors border-b border-gray-100 dark:border-white/5 last:border-0 ${
                        index === config.highlightedIndex ? 'bg-[#00F0FF]/10 dark:bg-[#00F0FF]/20' : ''
                      }`}
                      style={{ fontFamily: "'Inter', sans-serif" }}
                    >
                      {suggestion.display_name}
                    </li>
                  ))}
                </ul>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <motion.div 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-8 flex justify-end"
        >
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            disabled={!formData[config.field].trim() || !config.selectedLocation}
            onClick={() => setCurrentStep(config.nextStep)}
            className="px-8 py-4 rounded-full bg-[#00F0FF]/10 text-[#00F0FF] border border-[#00F0FF]/30 font-medium flex items-center gap-2 hover:bg-[#00F0FF]/20 transition-all shadow-[0_0_20px_rgba(0,240,255,0.2)] disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Continue
            <ArrowRight className="h-5 w-5" />
          </motion.button>
        </motion.div>
      </div>
    );
  };


  return (
    <section className="min-h-screen pt-[120px] pb-24 px-8 relative overflow-hidden">
      {/* Background ambient lights */}
      <div className="absolute top-1/4 left-10 h-96 w-96 rounded-full bg-[#00F0FF]/5 dark:bg-[#00F0FF]/10 blur-[150px]" />
      <div className="absolute bottom-1/4 right-10 h-96 w-96 rounded-full bg-[#8A2BE2]/5 dark:bg-[#8A2BE2]/10 blur-[150px]" />

      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          whileInView={{ y: 0, opacity: 1 }}
          viewport={{ once: true }}
          className="text-center mb-20"
        >
          <h2 
            className="text-6xl md:text-7xl font-black mb-6 bg-gradient-to-r from-gray-900 dark:from-white to-gray-500 dark:to-white/60 bg-clip-text text-transparent"
            style={{ fontFamily: "'Archivo Black', sans-serif" }}
          >
            CRAFT YOUR JOURNEY
          </h2>
          <p className="text-xl text-gray-500 dark:text-white/60" style={{ fontFamily: "'Inter', sans-serif" }}>
            Answer a few questions and let our AI agents create your perfect itinerary
          </p>
        </motion.div>

        {/* Progress Indicator */}
        <div className="flex justify-center gap-3 mb-16">
          {steps.map((step, index) => (
            <motion.div
              key={step.id}
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: index * 0.1 }}
              className={`h-2 rounded-full transition-all duration-500 ${
                index <= currentStep 
                  ? "w-12 bg-gradient-to-r from-[#00F0FF] to-[#8A2BE2]" 
                  : "w-6 bg-white/10"
              }`}
            />
          ))}
        </div>

        {/* Form Container - Glassmorphism */}
        <motion.div
          layout
          className="backdrop-blur-xl bg-white/80 dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-[32px] p-12 shadow-[0_8px_32px_rgba(0,0,0,0.08)] dark:shadow-[0_8px_32px_rgba(0,0,0,0.4)]"
        >
          <motion.div
            key={currentStep}
            initial={{ x: 100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -100, opacity: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h3 
              className="text-3xl font-bold text-gray-900 dark:text-white mb-8"
              style={{ fontFamily: "'Space Grotesk', sans-serif" }}
            >
              {steps[currentStep].title}
            </h3>

            {/* Step 0: Budget Selection */}
            {currentStep === 0 && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {budgetOptions.map((option) => (
                  <motion.button
                    key={option.id}
                    whileHover={{ scale: 1.03, y: -4 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleSelect("budget", option.id)}
                    className={`group relative p-8 rounded-[24px] border transition-all duration-300 ${
                      formData.budget === option.id
                        ? "bg-black/10 dark:bg-white/10 border-gray-400 dark:border-white/30 shadow-[0_0_30px_rgba(0,0,0,0.1)] dark:shadow-[0_0_30px_rgba(255,255,255,0.1)]"
                        : "bg-black/5 dark:bg-white/5 border-gray-200 dark:border-white/10 hover:border-gray-300 dark:hover:border-white/20"
                    }`}
                  >
                    <div className={`h-16 w-16 rounded-2xl bg-gradient-to-br ${option.gradient} flex items-center justify-center mb-6 shadow-lg`}>
                      <option.icon className="h-8 w-8 text-white" />
                    </div>
                    <h4 className="text-2xl font-bold text-gray-900 dark:text-white mb-2" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>
                      {option.label}
                    </h4>
                    <p className="text-gray-500 dark:text-white/60" style={{ fontFamily: "'Inter', sans-serif" }}>
                      {option.desc}
                    </p>
                  </motion.button>
                ))}
              </div>
            )}

            {/* Step 1: Lifestyle Selection */}
            {currentStep === 1 && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {lifestyleOptions.map((option) => (
                  <motion.button
                    key={option.id}
                    whileHover={{ scale: 1.03, y: -4 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleSelect("lifestyle", option.id)}
                    className={`group relative p-8 rounded-[24px] border transition-all duration-300 ${
                      formData.lifestyle === option.id
                        ? "bg-black/10 dark:bg-white/10 border-gray-400 dark:border-white/30 shadow-[0_0_30px_rgba(0,0,0,0.1)] dark:shadow-[0_0_30px_rgba(255,255,255,0.1)]"
                        : "bg-black/5 dark:bg-white/5 border-gray-200 dark:border-white/10 hover:border-gray-300 dark:hover:border-white/20"
                    }`}
                  >
                    <div className={`h-16 w-16 rounded-2xl bg-gradient-to-br ${option.gradient} flex items-center justify-center mb-6 shadow-lg`}>
                      <option.icon className="h-8 w-8 text-white" />
                    </div>
                    <h4 className="text-2xl font-bold text-gray-900 dark:text-white mb-2" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>
                      {option.label}
                    </h4>
                    <p className="text-gray-500 dark:text-white/60" style={{ fontFamily: "'Inter', sans-serif" }}>
                      {option.desc}
                    </p>
                  </motion.button>
                ))}
              </div>
            )}

            {/* Step 2: Vacation Type Selection */}
            {currentStep === 2 && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {vacationTypeOptions.map((option) => (
                  <motion.button
                    key={option.id}
                    whileHover={{ scale: 1.03, y: -4 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleSelect("vacationType", option.id)}
                    className={`group relative overflow-hidden h-80 rounded-[24px] border transition-all duration-300 ${
                      formData.vacationType === option.id
                        ? "border-white/30 shadow-[0_0_30px_rgba(255,255,255,0.1)]"
                        : "border-white/10 hover:border-white/20"
                    }`}
                  >
                    <Image 
                      src={option.image} 
                      alt={option.label}
                      fill
                      sizes="(max-width: 768px) 100vw, 33vw"
                      className="object-cover"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black via-black/60 to-transparent" />
                    <div className="absolute bottom-0 left-0 right-0 p-6">
                      <div className="flex items-center gap-3 mb-2">
                        <div className="h-12 w-12 rounded-xl bg-white/10 backdrop-blur-sm flex items-center justify-center border border-white/20">
                          <option.icon className="h-6 w-6 text-white" />
                        </div>
                        <h4 className="text-2xl font-bold text-white" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>
                          {option.label}
                        </h4>
                      </div>
                      <p className="text-white/80" style={{ fontFamily: "'Inter', sans-serif" }}>
                        {option.desc}
                      </p>
                    </div>
                  </motion.button>
                ))}
              </div>
            )}

            {/* Step 3: Origin Input (Nominatim Autocomplete) */}
            {currentStep === 3 && renderLocationStep({
              field: "origin",
              inputValue: originInput,
              setInputValue: setOriginInput,
              suggestions: originSuggestions,
              setSuggestions: setOriginSuggestions,
              isLoading: originLoading,
              selectedLocation: selectedOrigin,
              setSelectedLocation: setSelectedOrigin,
              highlightedIndex: originHighlight,
              setHighlightedIndex: setOriginHighlight,
              placeholder: "Your departure city (e.g., Bucharest)",
              icon: Plane,
              iconColor: "#8A2BE2",
              focusColor: "#8A2BE2",
              nextStep: 4,
            })}

            {/* Step 4: Destination Input (Nominatim Autocomplete) */}
            {currentStep === 4 && renderLocationStep({
              field: "destination",
              inputValue: destInput,
              setInputValue: setDestInput,
              suggestions: destSuggestions,
              setSuggestions: setDestSuggestions,
              isLoading: destLoading,
              selectedLocation: selectedDest,
              setSelectedLocation: setSelectedDest,
              highlightedIndex: destHighlight,
              setHighlightedIndex: setDestHighlight,
              placeholder: "Where do you want to go?",
              icon: MapPin,
              iconColor: "#00F0FF",
              focusColor: "#00F0FF",
              nextStep: 5,
            })}

            {/* Step 5: Travel Dates */}
            {currentStep === 5 && (
              <div className="max-w-2xl mx-auto space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Check-in */}
                  <div>
                    <label className="block text-sm font-medium text-gray-400 dark:text-white/40 mb-3 uppercase tracking-wider" style={{ fontFamily: "'Inter', sans-serif" }}>
                      Check-in
                    </label>
                    <div className="relative">
                      <CalendarDays className="absolute left-5 top-1/2 -translate-y-1/2 h-5 w-5 text-[#00F0FF] pointer-events-none" />
                      <input
                        type="date"
                        value={formData.startDate}
                        min={today}
                        onChange={(e) => {
                          handleInputChange("startDate", e.target.value);
                          // Auto-clear end date if it becomes invalid
                          if (formData.endDate && e.target.value >= formData.endDate) {
                            handleInputChange("endDate", "");
                          }
                        }}
                        className="w-full bg-black/5 dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-[16px] pl-14 pr-6 py-5 text-gray-900 dark:text-white text-lg focus:outline-none focus:border-[#00F0FF]/50 focus:shadow-[0_0_20px_rgba(0,240,255,0.15)] transition-all appearance-none [color-scheme:dark]"
                        style={{ fontFamily: "'Inter', sans-serif" }}
                        autoFocus
                      />
                    </div>
                  </div>

                  {/* Check-out */}
                  <div>
                    <label className="block text-sm font-medium text-gray-400 dark:text-white/40 mb-3 uppercase tracking-wider" style={{ fontFamily: "'Inter', sans-serif" }}>
                      Check-out
                    </label>
                    <div className="relative">
                      <CalendarDays className="absolute left-5 top-1/2 -translate-y-1/2 h-5 w-5 text-[#8A2BE2] pointer-events-none" />
                      <input
                        type="date"
                        value={formData.endDate}
                        min={formData.startDate || today}
                        onChange={(e) => handleInputChange("endDate", e.target.value)}
                        disabled={!formData.startDate}
                        className="w-full bg-black/5 dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-[16px] pl-14 pr-6 py-5 text-gray-900 dark:text-white text-lg focus:outline-none focus:border-[#8A2BE2]/50 focus:shadow-[0_0_20px_rgba(138,43,226,0.15)] transition-all appearance-none [color-scheme:dark] disabled:opacity-40 disabled:cursor-not-allowed"
                        style={{ fontFamily: "'Inter', sans-serif" }}
                      />
                    </div>
                  </div>
                </div>

                {/* Trip duration badge */}
                {tripDays > 0 && !dateError && (
                  <motion.div
                    initial={{ opacity: 0, y: 5 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center"
                  >
                    <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#00F0FF]/10 border border-[#00F0FF]/20 text-[#00F0FF] text-sm font-medium">
                      <CalendarDays className="h-4 w-4" />
                      {tripDays} {tripDays === 1 ? "day" : "days"} trip
                    </span>
                  </motion.div>
                )}

                {/* Error message */}
                {dateError && (
                  <motion.div
                    initial={{ opacity: 0, y: 5 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex items-center gap-2 text-red-400 text-sm bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3"
                    style={{ fontFamily: "'Inter', sans-serif" }}
                  >
                    <AlertTriangle className="h-4 w-4 flex-shrink-0" />
                    {dateError}
                  </motion.div>
                )}

                <motion.div 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-4 flex justify-end"
                >
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    disabled={!datesValid}
                    onClick={() => setCurrentStep(6)}
                    className="px-8 py-4 rounded-full bg-[#00F0FF]/10 text-[#00F0FF] border border-[#00F0FF]/30 font-medium flex items-center gap-2 hover:bg-[#00F0FF]/20 transition-all shadow-[0_0_20px_rgba(0,240,255,0.2)] disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Continue
                    <ArrowRight className="h-5 w-5" />
                  </motion.button>
                </motion.div>
              </div>
            )}

            {/* Step 6: Travelers Input */}
            {currentStep === 6 && (
              <div className="max-w-2xl mx-auto space-y-8">
                <div className="relative">
                  <Users className="absolute left-6 top-1/2 -translate-y-1/2 h-6 w-6 text-[#8A2BE2]" />
                  <input
                    type="number"
                    value={formData.travelers}
                    onChange={(e) => handleInputChange("travelers", e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && formData.travelers) {
                        handleSubmitForm();
                      }
                    }}
                    placeholder="Number of travelers"
                    min="1"
                    className="w-full bg-black/5 dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-[20px] pl-16 pr-6 py-6 text-gray-900 dark:text-white text-xl placeholder:text-gray-400 dark:placeholder:text-white/40 focus:outline-none focus:border-[#8A2BE2]/50 focus:shadow-[0_0_30px_rgba(138,43,226,0.2)] transition-all"
                    style={{ fontFamily: "'Inter', sans-serif" }}
                    autoFocus
                  />
                </div>

                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleSubmitForm}
                  disabled={!formData.destination || !formData.travelers || !formData.origin || !datesValid}
                  className="w-full py-6 rounded-[20px] bg-gradient-to-r from-[#00F0FF] to-[#8A2BE2] text-white text-xl font-bold flex items-center justify-center gap-3 shadow-[0_0_40px_rgba(0,240,255,0.3)] disabled:opacity-50 disabled:cursor-not-allowed"
                  style={{ fontFamily: "'Space Grotesk', sans-serif" }}
                >
                  Generate My Itinerary
                  <ArrowRight className="h-6 w-6" />
                </motion.button>
              </div>
            )}
          </motion.div>

          {/* Navigation */}
          {currentStep > 0 && currentStep <= 6 && (
            <motion.button
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              onClick={() => setCurrentStep(currentStep - 1)}
              className="mt-8 text-gray-500 dark:text-white/60 hover:text-gray-900 dark:hover:text-white transition-colors flex items-center gap-2"
              style={{ fontFamily: "'Inter', sans-serif" }}
            >
              ← Back
            </motion.button>
          )}
        </motion.div>
      </div>
    </section>
  );
}
