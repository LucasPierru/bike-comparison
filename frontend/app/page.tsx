import { getBikes, getBikeTypes } from "@/requests/bike";
import { BikeCard } from "@/components/bike-card/bike-card";
import { getTypeNameFromSlug } from "@/lib/utils";

export default async function Home() {
  const { bikes, error } = await getBikes();
  const { bikeTypes } = await getBikeTypes();

  const types = bikeTypes?.map((type) => ({
    name: getTypeNameFromSlug(type),
    value: type,
  }));

  console.log({ types });

  return (
    <div className="min-h-screen p-8 pb-20 sm:p-20">
      <main className="grid grid-cols-4 gap-8 row-start-2 items-center sm:items-start">
        {bikes && bikes.map((bike) => <BikeCard key={bike._id} bike={bike} />)}
      </main>
    </div>
  );
}
