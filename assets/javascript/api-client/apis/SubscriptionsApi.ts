/* tslint:disable */
/* eslint-disable */
/**
 * bmt-gpt-saas
 * The most amazing SaaS application the world has ever seen
 *
 * The version of the OpenAPI document: 0.1.0
 *
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */


import * as runtime from '../runtime';
import type {
  CreateCheckout,
  ProductWithMetadata,
} from '../models';
import {
    CreateCheckoutFromJSON,
    CreateCheckoutToJSON,
    ProductWithMetadataFromJSON,
    ProductWithMetadataToJSON,
} from '../models';

export interface CreateCheckoutSessionRequest {
    teamSlug: string;
    createCheckout: CreateCheckout;
}

export interface CreatePortalSessionRequest {
    teamSlug: string;
}

/**
 * 
 */
export class SubscriptionsApi extends runtime.BaseAPI {

    /**
     */
    async activeProductsListRaw(initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<runtime.ApiResponse<ProductWithMetadata>> {
        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        if (this.configuration && this.configuration.apiKey) {
            headerParameters["Authorization"] = this.configuration.apiKey("Authorization"); // ApiKeyAuth authentication
        }

        if (this.configuration && (this.configuration.username !== undefined || this.configuration.password !== undefined)) {
            headerParameters["Authorization"] = "Basic " + btoa(this.configuration.username + ":" + this.configuration.password);
        }
        const response = await this.request({
            path: `/subscriptions/api/active-products/`,
            method: 'GET',
            headers: headerParameters,
            query: queryParameters,
        }, initOverrides);

        return new runtime.JSONApiResponse(response, (jsonValue) => ProductWithMetadataFromJSON(jsonValue));
    }

    /**
     */
    async activeProductsList(initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<ProductWithMetadata> {
        const response = await this.activeProductsListRaw(initOverrides);
        return await response.value();
    }

    /**
     */
    async createCheckoutSessionRaw(requestParameters: CreateCheckoutSessionRequest, initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<runtime.ApiResponse<string>> {
        if (requestParameters.teamSlug === null || requestParameters.teamSlug === undefined) {
            throw new runtime.RequiredError('teamSlug','Required parameter requestParameters.teamSlug was null or undefined when calling createCheckoutSession.');
        }

        if (requestParameters.createCheckout === null || requestParameters.createCheckout === undefined) {
            throw new runtime.RequiredError('createCheckout','Required parameter requestParameters.createCheckout was null or undefined when calling createCheckoutSession.');
        }

        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        headerParameters['Content-Type'] = 'application/json';

        if (this.configuration && this.configuration.apiKey) {
            headerParameters["Authorization"] = this.configuration.apiKey("Authorization"); // ApiKeyAuth authentication
        }

        if (this.configuration && (this.configuration.username !== undefined || this.configuration.password !== undefined)) {
            headerParameters["Authorization"] = "Basic " + btoa(this.configuration.username + ":" + this.configuration.password);
        }
        const response = await this.request({
            path: `/a/{team_slug}/subscription/stripe/api/create-checkout-session/`.replace(`{${"team_slug"}}`, encodeURIComponent(String(requestParameters.teamSlug))),
            method: 'POST',
            headers: headerParameters,
            query: queryParameters,
            body: CreateCheckoutToJSON(requestParameters.createCheckout),
        }, initOverrides);

        return new runtime.TextApiResponse(response) as any;
    }

    /**
     */
    async createCheckoutSession(requestParameters: CreateCheckoutSessionRequest, initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<string> {
        const response = await this.createCheckoutSessionRaw(requestParameters, initOverrides);
        return await response.value();
    }

    /**
     */
    async createPortalSessionRaw(requestParameters: CreatePortalSessionRequest, initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<runtime.ApiResponse<string>> {
        if (requestParameters.teamSlug === null || requestParameters.teamSlug === undefined) {
            throw new runtime.RequiredError('teamSlug','Required parameter requestParameters.teamSlug was null or undefined when calling createPortalSession.');
        }

        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        if (this.configuration && this.configuration.apiKey) {
            headerParameters["Authorization"] = this.configuration.apiKey("Authorization"); // ApiKeyAuth authentication
        }

        if (this.configuration && (this.configuration.username !== undefined || this.configuration.password !== undefined)) {
            headerParameters["Authorization"] = "Basic " + btoa(this.configuration.username + ":" + this.configuration.password);
        }
        const response = await this.request({
            path: `/a/{team_slug}/subscription/stripe/api/create-portal-session/`.replace(`{${"team_slug"}}`, encodeURIComponent(String(requestParameters.teamSlug))),
            method: 'POST',
            headers: headerParameters,
            query: queryParameters,
        }, initOverrides);

        return new runtime.TextApiResponse(response) as any;
    }

    /**
     */
    async createPortalSession(requestParameters: CreatePortalSessionRequest, initOverrides?: RequestInit | runtime.InitOverrideFunction): Promise<string> {
        const response = await this.createPortalSessionRaw(requestParameters, initOverrides);
        return await response.value();
    }

}
