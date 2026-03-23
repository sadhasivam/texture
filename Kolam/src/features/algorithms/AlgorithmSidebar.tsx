import { useState, useEffect, useMemo } from 'react';
import { useAlgorithms, useAlgorithmMetadata } from './useAlgorithms';
import AlgorithmCard from './AlgorithmCard';
import type { AlgorithmMetadata, AlgorithmSummary } from '../../types/algorithm';
import './AlgorithmSidebar.css';

interface AlgorithmSidebarProps {
  selectedAlgorithmId?: string;
  onSelectAlgorithm: (metadata: AlgorithmMetadata) => void;
}

// Group -> Subgroup -> Algorithms
interface GroupedAlgorithms {
  [group: string]: {
    [subgroup: string]: AlgorithmSummary[];
  };
}

export default function AlgorithmSidebar({
  selectedAlgorithmId,
  onSelectAlgorithm,
}: AlgorithmSidebarProps) {
  const { data: algorithms, isLoading, error } = useAlgorithms();
  const [fetchingAlgorithmId, setFetchingAlgorithmId] = useState<string | null>(null);
  const { data: selectedMetadata } = useAlgorithmMetadata(fetchingAlgorithmId);

  // Track collapsed state for each group/subgroup
  const [collapsedGroups, setCollapsedGroups] = useState<Set<string>>(new Set());
  const [collapsedSubgroups, setCollapsedSubgroups] = useState<Set<string>>(new Set());

  // Group algorithms by group -> subgroup
  const groupedAlgorithms = useMemo(() => {
    if (!algorithms) return {};

    const grouped: GroupedAlgorithms = {};

    algorithms.forEach((algo) => {
      if (!grouped[algo.group]) {
        grouped[algo.group] = {};
      }
      if (!grouped[algo.group][algo.subgroup]) {
        grouped[algo.group][algo.subgroup] = [];
      }
      grouped[algo.group][algo.subgroup].push(algo);
    });

    return grouped;
  }, [algorithms]);

  // When metadata is loaded, pass it to parent
  useEffect(() => {
    if (selectedMetadata && selectedMetadata.id === fetchingAlgorithmId) {
      onSelectAlgorithm(selectedMetadata);
      setFetchingAlgorithmId(null);
    }
  }, [selectedMetadata, fetchingAlgorithmId, onSelectAlgorithm]);

  const handleSelectAlgorithm = (algorithmId: string) => {
    setFetchingAlgorithmId(algorithmId);
  };

  const toggleGroup = (group: string) => {
    setCollapsedGroups((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(group)) {
        newSet.delete(group);
      } else {
        newSet.add(group);
      }
      return newSet;
    });
  };

  const toggleSubgroup = (groupSubgroupKey: string) => {
    setCollapsedSubgroups((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(groupSubgroupKey)) {
        newSet.delete(groupSubgroupKey);
      } else {
        newSet.add(groupSubgroupKey);
      }
      return newSet;
    });
  };

  const formatGroupName = (group: string) => {
    if (group === 'supervised') return 'SUPERVISED';
    if (group === 'unsupervised') return 'UNSUPERVISED';
    if (group === 'anomaly_detection') return 'ANOMALY DETECTION';
    return group.split('_').map(word =>
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ').toUpperCase();
  };

  const formatSubgroupName = (subgroup: string) => {
    if (subgroup === 'both') return 'Both';
    if (subgroup === 'classification') return 'Classification';
    if (subgroup === 'regression') return 'Regression';
    if (subgroup === 'clustering') return 'Clustering';
    if (subgroup === 'dimensionality_reduction') return 'Dimensionality Reduction';
    if (subgroup === 'anomaly_detection') return 'Anomaly Detection';
    return subgroup.split('_').map(word =>
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  return (
    <aside className="algorithm-sidebar">
      <div className="sidebar-header">
        <h2>Algorithms</h2>
        <div className="algorithm-count">{algorithms?.length || 0} total</div>
      </div>

      <div className="sidebar-content">
        {isLoading && (
          <div className="sidebar-loading">
            <p>Loading algorithms...</p>
          </div>
        )}

        {error && (
          <div className="sidebar-error">
            <p>Failed to load algorithms</p>
          </div>
        )}

        {algorithms && algorithms.length === 0 && (
          <div className="sidebar-empty">
            <p>No algorithms available</p>
          </div>
        )}

        {Object.entries(groupedAlgorithms).map(([group, subgroups]) => {
          const isGroupCollapsed = collapsedGroups.has(group);
          const totalInGroup = Object.values(subgroups).reduce(
            (sum, algos) => sum + algos.length,
            0
          );

          return (
            <div key={group} className="algorithm-group">
              <button
                className="group-header"
                onClick={() => toggleGroup(group)}
              >
                <span className="group-icon">{isGroupCollapsed ? '▶' : '▼'}</span>
                <span className="group-name">{formatGroupName(group)}</span>
                <span className="group-count">{totalInGroup}</span>
              </button>

              {!isGroupCollapsed && (
                <div className="group-content">
                  {Object.entries(subgroups).map(([subgroup, algos]) => {
                    const subgroupKey = `${group}-${subgroup}`;
                    const isSubgroupCollapsed = collapsedSubgroups.has(subgroupKey);

                    return (
                      <div key={subgroupKey} className="algorithm-subgroup">
                        <button
                          className="subgroup-header"
                          onClick={() => toggleSubgroup(subgroupKey)}
                        >
                          <span className="subgroup-icon">{isSubgroupCollapsed ? '▶' : '▼'}</span>
                          <span className="subgroup-name">{formatSubgroupName(subgroup)}</span>
                          <span className="subgroup-count">{algos.length}</span>
                        </button>

                        {!isSubgroupCollapsed && (
                          <div className="subgroup-content">
                            {algos.map((algorithm) => (
                              <AlgorithmCard
                                key={algorithm.id}
                                algorithm={algorithm}
                                isSelected={algorithm.id === selectedAlgorithmId}
                                onSelect={() => handleSelectAlgorithm(algorithm.id)}
                              />
                            ))}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </aside>
  );
}
