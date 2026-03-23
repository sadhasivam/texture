package config

import (
	"fmt"
	"strings"

	"github.com/spf13/viper"
)

type Config struct {
	ClerkPublishableKey string `mapstructure:"clerk_publishable_key"`
	ClerkSecretKey      string `mapstructure:"clerk_secret_key"`
	Port                string `mapstructure:"port"`
	Environment         string `mapstructure:"environment"`
	WeaverGRPCURL       string `mapstructure:"weaver_grpc_url"`
	AlgorithmSpecsPath  string `mapstructure:"algorithm_specs_path"`
	DatasetStoragePath  string `mapstructure:"dataset_storage_path"`
}

var globalConfig *Config

func Init(cfgFile string) error {
	if cfgFile != "" {
		viper.SetConfigFile(cfgFile)
	} else {
		// Read from root .env (single source of truth)
		viper.SetConfigName(".env")
		viper.SetConfigType("env")
		viper.AddConfigPath("..") // Parent directory (texture/)
		viper.AddConfigPath(".")   // Fallback to current directory
	}

	// Environment variable support
	viper.SetEnvPrefix("") // No prefix
	viper.AutomaticEnv()
	viper.SetEnvKeyReplacer(strings.NewReplacer(".", "_"))

	// Set defaults
	viper.SetDefault("port", "8080")
	viper.SetDefault("environment", "development")
	viper.SetDefault("weaver_grpc_url", "localhost:50051")
	viper.SetDefault("algorithm_specs_path", "../algorithms")
	viper.SetDefault("dataset_storage_path", "../storage/datasets")

	// Read config file
	if err := viper.ReadInConfig(); err != nil {
		if _, ok := err.(viper.ConfigFileNotFoundError); !ok {
			return fmt.Errorf("failed to read config file: %w", err)
		}
		// Config file not found; use defaults and env vars
	}

	// Unmarshal to struct
	globalConfig = &Config{}
	if err := viper.Unmarshal(globalConfig); err != nil {
		return fmt.Errorf("failed to unmarshal config: %w", err)
	}

	return nil
}

func Get() *Config {
	if globalConfig == nil {
		panic("config not initialized - call config.Init() first")
	}
	return globalConfig
}
