"use server";

import { Bike } from "@/types/bike.types";
import { api } from "./api";

export const getBikes = async (
  type?: string,
  minPrice?: number,
  maxPrice?: number
): Promise<{
  bikes: Bike[] | null;
  error: unknown;
}> => {
  try {
    const response = await api(
      `/v1/bike?type=${type || ""}&minPrice=${minPrice || ""}&maxPrice=${
        maxPrice || ""
      }`,
      {
        method: "GET",
      }
    );
    const data = await response.json();
    const { bikes, error } = data;
    if (error) throw error;
    return { bikes, error: null };
  } catch (error) {
    return { bikes: null, error };
  }
};

export const getBikeTypes = async (): Promise<{
  bikeTypes: string[] | null;
  error: unknown;
}> => {
  try {
    const response = await api("/v1/bike/types", {
      method: "GET",
    });
    const data = await response.json();
    const { bikeTypes, error } = data;
    if (error) throw error;
    return { bikeTypes, error: null };
  } catch (error) {
    return { bikeTypes: null, error };
  }
};
