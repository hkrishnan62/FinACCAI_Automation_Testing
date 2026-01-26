package com.finaccai.mobile

import okhttp3.Interceptor
import okhttp3.Response

class AuthInterceptor : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val original = chain.request()
        val builder = original.newBuilder()

        // Add auth token if configured
        Config.AUTH_TOKEN?.let {
            builder.addHeader("Authorization", "Bearer $it")
        }

        builder.addHeader("User-Agent", "FinAccAI-Mobile/1.0")

        return chain.proceed(builder.build())
    }
}
