export class CompanyNotFoundError extends Error {
  constructor(message = "Company not found.") {
    super(message);
    this.name = "CompanyNotFoundError";
  }
}

export function isCompanyNotFoundError(error: unknown): error is CompanyNotFoundError {
  return error instanceof CompanyNotFoundError;
}
