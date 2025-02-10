"use server";

import { Bike } from "@/types/bike.types";
import { api } from "./api";

export const getBikes = async (): Promise<{
  bikes: Bike[] | null;
  error: unknown;
}> => {
  try {
    const response = await api("/v1/bike", {
      method: "GET",
      /* headers: {
          authorization: `Bearer ${token.value}`
        } */
    });
    const data = await response.json();
    const { bikes, error } = data;
    if (error) throw error;
    return { bikes, error: null };
  } catch (error) {
    return { bikes: null, error };
  }
};
