package main

import (
	"fmt"
	"os"

	"github.com/sadhasivam/texture/internal/config"
	"github.com/spf13/cobra"
)

var (
	cfgFile string

	rootCmd = &cobra.Command{
		Use:   "wrap",
		Short: "Loom - Texture backend service",
		Long: `Loom is the backend service for Texture, providing authentication,
data management, and orchestration for the ML platform.`,
		PersistentPreRunE: func(cmd *cobra.Command, args []string) error {
			return config.Init(cfgFile)
		},
	}
)

func init() {
	rootCmd.PersistentFlags().StringVar(&cfgFile, "config", "", "config file (default is .env)")
}

func Execute() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
