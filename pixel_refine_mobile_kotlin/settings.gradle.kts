pluginManagement {
    repositories {
        google {
            content {
                includeGroupByRegex("com\\.android.*")
                includeGroupByRegex("com\\.google.*")
                includeGroupByRegex("androidx.*")
            }
        }
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "pixel_refine_mobile_kotlin"
include(":composeApp")
include(":generic-ui-kotlin")
project(":generic-ui-kotlin").projectDir = file("../resources/GenericUILibraryKotlin")
