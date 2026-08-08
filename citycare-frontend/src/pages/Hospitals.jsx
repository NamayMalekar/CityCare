import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { Spinner, Banner } from '../components/ui';

export default function Hospitals() {
  const navigate = useNavigate();
  const [hospitals, setHospitals] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [selectedHospital, setSelectedHospital] = useState(null);
  const [loading, setLoading] = useState(true);
  const [banner, setBanner] = useState(null);

  useEffect(() => {
    async function loadHospitals() {
      setLoading(true);
      try {
        const [hList, dList] = await Promise.all([
          api.listHospitals(),
          api.listDoctors(),
        ]);
        setHospitals(hList);
        setDoctors(dList);
      } catch (err) {
        setBanner({ kind: 'error', text: err.message });
      } finally {
        setLoading(false);
      }
    }
    loadHospitals();
  }, []);

  const handleSelectHospital = (hospital) => {
    navigate('/book', { state: { hospitalId: hospital.id, hospitalName: hospital.name } });
  };

  if (loading) return <Spinner label="Discovering healthcare facilities…" />;

  return (
    <div className="mx-auto max-w-5xl px-5 py-8">
      {/* Header */}
      <div className="mb-8">
        <span className="inline-block rounded-full bg-pine/10 px-3 py-1 text-xs font-semibold text-pine">
          Multi-Hospital Network
        </span>
        <h1 className="mt-1 font-display text-3xl font-semibold tracking-tight text-ink">
          Select a Hospital Facility
        </h1>
        <p className="mt-1 text-sm text-sage">
          Choose a partner hospital to browse specialized doctors and available consultation slots.
        </p>
      </div>

      {banner && (
        <div className="mb-6">
          <Banner kind={banner.kind} onClose={() => setBanner(null)}>
            {banner.text}
          </Banner>
        </div>
      )}

      {hospitals.length === 0 ? (
        <div className="card p-8 text-center text-sage">
          No hospitals currently listed in the system. Check back soon!
        </div>
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {hospitals.map((h) => {
            const docCount = doctors.filter((d) => d.hospital_id === h.id).length;
            return (
              <div
                key={h.id}
                className="card p-6 flex flex-col justify-between hover:shadow-soft transition-all border border-mist hover:border-pine/30"
              >
                <div>
                  <span className="rounded-full bg-cream px-2.5 py-0.5 text-xs font-semibold text-pine">
                    {h.city}
                  </span>
                  <h2 className="mt-3 font-display text-xl font-semibold text-ink">
                    {h.name}
                  </h2>
                  <p className="mt-1 text-xs text-sage">{h.address}</p>

                  <div className="mt-4 pt-3 border-t border-mist text-xs text-ink/80 space-y-1">
                    <p>📞 {h.contact_phone || h.phone}</p>
                    <p>✉️ {h.email}</p>
                    <p className="mt-2 font-medium text-moss">
                      👨‍⚕️ {docCount} {docCount === 1 ? 'Doctor' : 'Doctors'} Available
                    </p>
                  </div>
                </div>

                <button
                  onClick={() => handleSelectHospital(h)}
                  className="btn-primary w-full mt-6 text-sm"
                >
                  Book at this Hospital
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
